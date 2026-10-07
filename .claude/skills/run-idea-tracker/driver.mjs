// Idea Tracker driver - launches Streamlit + FastAPI and drives via chromium-cli
// Usage: node driver.mjs [command] [args]
// Commands: screenshot, create-idea, metrics, quit

import { spawn } from 'node:child_process';
import fs from 'node:fs';
import path from 'node:path';
import { execSync } from 'node:child_process';

// Configuration
const PORT = 8503;
const SCREENSHOTS_DIR = path.join(process.cwd(), 'screenshots');
const TIMEOUT = 10000; // 10 seconds

// Helper functions
async function wait(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function checkCommand(cmd) {
  try {
    execSync(cmd, { stdio: 'pipe' });
    return true;
  } catch (e) {
    return false;
  }
}

async function runCommand(command, args = [], options = {}) {
  return new Promise((resolve, reject) => {
    const child = spawn(command, args, {
      stdio: 'pipe',
      ...options
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (data) => stdout += data.toString());
    child.stderr.on('data', (data) => stderr += data.toString());
    child.on('close', (code) => {
      if (code === 0) {
        resolve({ stdout, stderr, code });
      } else {
        reject(new Error(`${command} failed: ${stderr || stdout}`));
      }
    });
  });
}

async function launchFastAPI() {
  console.log('Launching FastAPI server...');
  // Launch uvicorn in background
  const fastApiProcess = spawn('uv', ['run', 'uvicorn', 'idea_tracker.main:app', '--host', '127.0.0.1', '--port', PORT.toString()], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: true
  });

  // Wait for server to start
  await wait(2000);

  // Verify server is responding
  try {
    const response = await fetch(`http://127.0.0.1:${PORT}/health`);
    if (!response.ok) throw new Error('Health check failed');
    console.log('FastAPI server ready');
    return fastApiProcess;
  } catch (e) {
    console.error('FastAPI health check failed:', e.message);
    fastApiProcess.kill();
    throw e;
  }
}

async function launchStreamlit() {
  console.log('Launching Streamlit...');
  // Launch Streamlit in headless mode
  const streamlitProcess = spawn('uv', ['run', 'streamlit', 'run', 'app.py', '--server.port', PORT.toString(), '--server.headless', 'true', '--browser.gatherUsageStat', 'false'], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: true
  });

  // Wait for Streamlit to start
  await wait(3000);

  // Verify Streamlit is responding
  try {
    const response = await fetch(`http://127.0.0.1:${PORT}`);
    if (!response.ok) throw new Error('Streamlit health check failed');
    console.log('Streamlit ready');
    return streamlitProcess;
  } catch (e) {
    console.error('Streamlit health check failed:', e.message);
    streamlitProcess.kill();
    throw e;
  }
}

async function launchChromium() {
  console.log('Launching chromium-cli...');
  // Launch chromium-cli with viewport
  const chromiumProcess = spawn('npx', ['chromium-cli', '--headless', '--disable-gpu', '--window-size=1920,1080', '--screenshot', path.join(SCREENSHOTS_DIR, `screenshot-${Date.now()}.png`)], {
    stdio: ['pipe', 'pipe', 'inherit']
    });

  // Wait for chromium to start
  await wait(2000);

  // Navigate to Streamlit app
  try {
    await runCommand('npx', ['chromium-cli', '--url', `http://localhost:${PORT}`]);
    console.log('Chromium navigated to app');
    return chromiumProcess;
  } catch (e) {
    console.error('Failed to navigate to app:', e.message);
    chromiumProcess.kill();
    throw e;
  }
}

async function createIdea(title, description, tags = []) {
  console.log(`Creating idea: ${title}`);
  const tagParam = tags.length ? `&tags=${encodeURIComponent(tags.join(','))}` : '';
  const response = await fetch(`http://127.0.0.1:${PORT}/api/ideas`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ title, raw_description: description, tags })
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(`API create failed: ${response.status} ${text}`);
  }

  const idea = await response.json();
  console.log('Idea created:', idea.id);
  return idea;
}

async function getMetrics() {
  console.log('Fetching metrics...');
  const response = await fetch(`http://127.0.0.1:${PORT}/api/stats`);
  if (!response.ok) throw new Error('Metrics fetch failed');
  return await response.json();
}

async function takeScreenshot() {
  console.log('Taking screenshot...');
  const timestamp = Date.now();
  const screenshotPath = path.join(SCREENSHOTS_DIR, `screenshot-${timestamp}.png`);

  try {
    await runCommand('npx', ['chromium-cli', '--screenshot', screenshotPath, '--url', `http://localhost:${PORT}`]);
    console.log(`Screenshot saved: ${screenshotPath}`);
    return screenshotPath;
  } catch (e) {
    console.error('Screenshot failed:', e.message);
    throw e;
  }
}

async function quit() {
  console.log('Shutting down...');
  // Gracefully kill processes
  try {
    await runCommand('pkill', ['-f', 'uvicorn']);
    await runCommand('pkill', ['-f', 'streamlit']);
    await runCommand('pkill', ['-f', 'chromium-cli']);
  } catch (e) {
    // Ignore kill errors
  }
  console.log('All processes stopped');
}

// Main execution
async function main(args) {
  try {
    // Setup screenshots directory
    fs.mkdirSync(SCREENSHOTS_DIR, { recursive: true });

    // Check prerequisites
    if (!(await checkCommand('python3 --version'))) {
      throw new Error('Python 3 not found');
    }
    if (!(await checkCommand('uv --version'))) {
      throw new Error('uv not found - install with: pip install uv');
    }
    if (!(await checkCommand('npx --version'))) {
      throw new Error('npx not found - install Node.js');
    }

    // Launch services
    const [fastApi, streamlit, chromium] = await Promise.all([
      launchFastAPI(),
      launchStreamlit(),
      launchChromium()
    ]);

    // Handle command
    const command = args[0];
    const commandArgs = args.slice(1);

    switch (command) {
      case 'screenshot':
        await takeScreenshot();
        break;
      case 'create-idea':
        if (commandArgs.length < 2) {
          throw new Error('Usage: create-idea "Title" "Description" [--tags tag1,tag2]');
        }
        const title = commandArgs[0];
        const description = commandArgs[1];
        const tags = commandArgs.includes('--tags') ?
          commandArgs[commandArgs.indexOf('--tags') + 1]?.split(',').filter(Boolean) : [];
        await createIdea(title, description, tags);
        break;
      case 'metrics':
        const metrics = await getMetrics();
        console.log('Metrics:', JSON.stringify(metrics, null, 2));
        break;
      case 'quit':
        await quit();
        process.exit(0);
        break;
      default:
        console.log('Launching app without command...');
        console.log('Available commands: screenshot, create-idea, metrics, quit');
    }

    // Keep running if no quit command
    if (command !== 'quit') {
      console.log('Driver running. Press Ctrl+C to exit.');
      // Keep process alive
      await new Promise(() => {});
    }
  } catch (e) {
    console.error('Driver error:', e.message);
    process.exit(1);
  }
}

// Parse args
const args = process.argv.slice(2);
main(args);