/*
 This file is part of wger Workout Manager.

 wger Workout Manager is free software: you can redistribute it and/or modify
 it under the terms of the GNU Affero General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 wger Workout Manager is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU Affero General Public License
 */

/*
 * wger Countdown Timer for timed exercises
 */

'use strict';

class CountdownTimer {
  constructor(container, options = {}) {
    this.container = typeof container === 'string'
      ? document.querySelector(container)
      : container;

    this.duration = options.duration || 60; // Duration in seconds
    this.onComplete = options.onComplete || null;
    this.onTick = options.onTick || null;
    this.autoStart = options.autoStart || false;
    this.showMilliseconds = options.showMilliseconds || false;

    this.timeRemaining = this.duration;
    this.isRunning = false;
    this.isPaused = false;
    this.intervalId = null;
    this.audioContext = null;

    this.init();
  }

  init() {
    this.render();
    this.bindEvents();
    this.updateDisplay();

    if (this.autoStart) {
      this.start();
    }
  }

  render() {
    this.container.innerHTML = `
      <div class="countdown-timer">
        <div class="timer-circle">
          <svg class="timer-svg" viewBox="0 0 100 100">
            <circle class="timer-bg" cx="50" cy="50" r="45" />
            <circle class="timer-progress" cx="50" cy="50" r="45" />
          </svg>
          <div class="timer-display">
            <span class="timer-time">00:00</span>
          </div>
        </div>
        <div class="timer-controls">
          <button class="btn btn-success timer-btn timer-start" title="Start">
            <i class="fa-solid fa-play"></i>
          </button>
          <button class="btn btn-warning timer-btn timer-pause" title="Pause" style="display: none;">
            <i class="fa-solid fa-pause"></i>
          </button>
          <button class="btn btn-secondary timer-btn timer-reset" title="Reset">
            <i class="fa-solid fa-rotate-left"></i>
          </button>
        </div>
      </div>
    `;

    // Cache DOM elements
    this.elements = {
      circle: this.container.querySelector('.timer-progress'),
      timeDisplay: this.container.querySelector('.timer-time'),
      startBtn: this.container.querySelector('.timer-start'),
      pauseBtn: this.container.querySelector('.timer-pause'),
      resetBtn: this.container.querySelector('.timer-reset'),
      timerCircle: this.container.querySelector('.timer-circle')
    };

    // Calculate circle circumference for progress animation
    this.circumference = 2 * Math.PI * 45;
    this.elements.circle.style.strokeDasharray = this.circumference;
    this.elements.circle.style.strokeDashoffset = 0;
  }

  bindEvents() {
    this.elements.startBtn.addEventListener('click', () => this.start());
    this.elements.pauseBtn.addEventListener('click', () => this.pause());
    this.elements.resetBtn.addEventListener('click', () => this.reset());
  }

  start() {
    if (this.isRunning) return;

    this.isRunning = true;
    this.isPaused = false;

    this.elements.startBtn.style.display = 'none';
    this.elements.pauseBtn.style.display = 'inline-block';

    this.lastTick = Date.now();
    this.intervalId = setInterval(() => this.tick(), 100);
  }

  pause() {
    if (!this.isRunning) return;

    this.isRunning = false;
    this.isPaused = true;

    this.elements.startBtn.style.display = 'inline-block';
    this.elements.pauseBtn.style.display = 'none';

    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  reset() {
    this.pause();
    this.timeRemaining = this.duration;
    this.isPaused = false;
    this.updateDisplay();
    this.elements.timerCircle.classList.remove('timer-complete');
  }

  tick() {
    const now = Date.now();
    const delta = (now - this.lastTick) / 1000;
    this.lastTick = now;

    this.timeRemaining -= delta;

    if (this.timeRemaining <= 0) {
      this.timeRemaining = 0;
      this.complete();
    }

    this.updateDisplay();

    if (this.onTick) {
      this.onTick(this.timeRemaining);
    }
  }

  updateDisplay() {
    // Update time display
    const minutes = Math.floor(this.timeRemaining / 60);
    const seconds = Math.floor(this.timeRemaining % 60);
    const timeString = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
    this.elements.timeDisplay.textContent = timeString;

    // Update progress circle
    const progress = this.timeRemaining / this.duration;
    const offset = this.circumference * (1 - progress);
    this.elements.circle.style.strokeDashoffset = offset;

    // Change color as time runs low
    if (this.timeRemaining <= 10 && this.timeRemaining > 5) {
      this.elements.circle.classList.add('timer-warning');
      this.elements.circle.classList.remove('timer-danger');
    } else if (this.timeRemaining <= 5) {
      this.elements.circle.classList.remove('timer-warning');
      this.elements.circle.classList.add('timer-danger');
    } else {
      this.elements.circle.classList.remove('timer-warning', 'timer-danger');
    }
  }

  complete() {
    this.pause();
    this.elements.timerCircle.classList.add('timer-complete');
    this.playCompletionSound();

    if (this.onComplete) {
      this.onComplete();
    }
  }

  playCompletionSound() {
    try {
      // Create audio context on demand (browsers require user interaction)
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }

      // Play a simple beep sequence
      const playBeep = (time, frequency, duration) => {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();

        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);

        oscillator.frequency.value = frequency;
        oscillator.type = 'sine';

        gainNode.gain.setValueAtTime(0.3, time);
        gainNode.gain.exponentialRampToValueAtTime(0.01, time + duration);

        oscillator.start(time);
        oscillator.stop(time + duration);
      };

      const now = this.audioContext.currentTime;
      playBeep(now, 880, 0.15);
      playBeep(now + 0.2, 880, 0.15);
      playBeep(now + 0.4, 1760, 0.3);
    } catch (e) {
      console.log('Audio not available:', e);
    }
  }

  setDuration(seconds) {
    this.duration = seconds;
    this.reset();
  }

  destroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
    if (this.audioContext) {
      this.audioContext.close();
    }
    this.container.innerHTML = '';
  }
}


/*
 * Timer initialization for workout pages
 * Checks for timed exercises and initializes timers
 */
function wgerInitTimers() {
  // Find all timer containers on the page
  const timerContainers = document.querySelectorAll('[data-timer-duration]');

  timerContainers.forEach(container => {
    const duration = parseInt(container.dataset.timerDuration, 10);
    const unitType = container.dataset.timerUnitType;

    // Only initialize timer for TIME unit types
    if (unitType === 'TIME' && duration > 0) {
      new CountdownTimer(container, {
        duration: duration,
        onComplete: () => {
          console.log('Timer completed!');
        }
      });
    }
  });
}


/*
 * Utility function to create a timer programmatically
 */
function wgerCreateTimer(selector, durationSeconds, options = {}) {
  return new CountdownTimer(selector, {
    duration: durationSeconds,
    ...options
  });
}


// Auto-initialize timers when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
  wgerInitTimers();
  // Use button-based timer injection on routine pages
  wgerInitTimerButtons();
});


/*
 * Workout Page Timer Injection
 * Automatically detects timed exercises in the React workout UI and injects timers
 * Only runs on routine view pages to avoid performance issues
 */
function wgerInitWorkoutTimerInjection() {
  // Only run on routine/workout pages
  const path = window.location.pathname;
  if (!path.includes('/routine/') && !path.includes('/workout/')) {
    return;
  }

  // Time-based unit names (matches the RepetitionUnit fixtures)
  const TIME_UNITS = ['seconds', 'minutes', 'second', 'minute', 'sec', 'min'];

  // Track if we've already injected timers
  let timersInjected = false;
  let debounceTimer = null;

  // Debounced injection function
  function debouncedInject() {
    if (debounceTimer) clearTimeout(debounceTimer);
    debounceTimer = setTimeout(injectTimersIntoWorkout, 500);
  }

  // Watch for DOM changes (React renders dynamically)
  const observer = new MutationObserver(function(mutations) {
    // Only re-run if we haven't injected yet
    if (!timersInjected) {
      debouncedInject();
    }
  });

  // Start observing the document for React component renders
  observer.observe(document.body, {
    childList: true,
    subtree: true
  });

  // Also run with delays for React hydration
  setTimeout(injectTimersIntoWorkout, 1000);
  setTimeout(injectTimersIntoWorkout, 2500);

  function injectTimersIntoWorkout() {
    // Skip if already injected
    if (document.querySelector('.wger-exercise-timer')) {
      timersInjected = true;
      observer.disconnect(); // Stop watching once done
      return;
    }

    // Look for exercise entries that mention time units
    // The React UI typically shows something like "60 Seconds" or "2 Minutes"

    // Search text-containing elements (limited scope)
    const allElements = document.querySelectorAll('div, span, td, li, p');

    // Find all elements that directly contain "X Seconds" or "X Minutes" text
    const matches = [];

    allElements.forEach(el => {
      // Skip if already has a timer
      if (el.querySelector('.wger-exercise-timer') || el.classList.contains('wger-exercise-timer')) return;

      // Check direct text content only (not nested children)
      // This helps find the most specific element
      let hasDirectTimeText = false;
      let duration = null;
      let unitName = null;

      // Check the element's own text (excluding children)
      const ownText = Array.from(el.childNodes)
        .filter(node => node.nodeType === Node.TEXT_NODE)
        .map(node => node.textContent)
        .join(' ');

      // Also check if this element has very little child content (meaning it's specific)
      const fullText = el.textContent;

      for (const unit of TIME_UNITS) {
        const regex = new RegExp(`(\\d+(?:\\.\\d+)?)\\s*${unit}`, 'i');

        // First try own text
        let match = ownText.match(regex);
        if (match) {
          hasDirectTimeText = true;
          duration = parseFloat(match[1]);
          unitName = unit;
          break;
        }

        // Then try full text but only for small elements (< 100 chars)
        if (fullText.length < 100) {
          match = fullText.match(regex);
          if (match) {
            duration = parseFloat(match[1]);
            unitName = unit;
            break;
          }
        }
      }

      if (duration && unitName) {
        matches.push({
          element: el,
          duration: duration,
          unitName: unitName,
          textLength: fullText.length,
          hasDirectText: hasDirectTimeText
        });
      }
    });

    // Sort by specificity: prefer direct text matches, then smaller text length
    matches.sort((a, b) => {
      if (a.hasDirectText !== b.hasDirectText) return b.hasDirectText - a.hasDirectText;
      return a.textLength - b.textLength;
    });

    // Inject timer for each unique match (avoid duplicates by tracking parent chains)
    const processedElements = new Set();

    matches.forEach(match => {
      const { element, duration, unitName } = match;

      // Skip if any parent already has a timer
      let parent = element;
      let skipThis = false;
      while (parent) {
        if (processedElements.has(parent)) {
          skipThis = true;
          break;
        }
        parent = parent.parentElement;
      }
      if (skipThis) return;

      // Mark this element and its parents as processed
      processedElements.add(element);

      // Convert to seconds if needed
      let durationSeconds = duration;
      if (unitName.startsWith('min')) {
        durationSeconds = duration * 60;
      }

      console.log('Timer injection: injecting timer for', durationSeconds, 'seconds next to:', element.textContent.substring(0, 50));

      // Create a compact inline timer container
      const timerContainer = document.createElement('div');
      timerContainer.className = 'wger-exercise-timer wger-exercise-timer-inline';
      timerContainer.style.cssText = 'display: inline-flex; align-items: center; margin-left: 10px; vertical-align: middle;';

      // Insert right after the element (as a sibling)
      if (element.nextSibling) {
        element.parentNode.insertBefore(timerContainer, element.nextSibling);
      } else {
        element.parentNode.appendChild(timerContainer);
      }

      // Initialize the timer with compact size
      new CountdownTimer(timerContainer, {
        duration: Math.round(durationSeconds),
        onComplete: () => {
          // Visual feedback on completion
          element.style.backgroundColor = '#d4edda';
          setTimeout(() => {
            element.style.backgroundColor = '';
          }, 2000);
        }
      });

      // Mark as injected and stop observer
      timersInjected = true;
      observer.disconnect();
    });
  }
}


/*
 * API-based Timer Injection (Alternative approach)
 * Fetches repetition unit info from API to determine if timer should show
 */
async function wgerFetchAndInjectTimers() {
  try {
    // Fetch repetition units from API
    const response = await fetch('/api/v2/setting-repetitionunit/');
    const data = await response.json();

    // Find TIME units
    const timeUnitIds = data.results
      .filter(unit => unit.unit_type === 'TIME')
      .map(unit => unit.id);

    console.log('Time-based unit IDs:', timeUnitIds);

    // Store globally for use by other functions
    window.wgerTimeUnitIds = timeUnitIds;
  } catch (e) {
    console.log('Could not fetch repetition units:', e);
  }
}

// Fetch time units on page load
document.addEventListener('DOMContentLoaded', wgerFetchAndInjectTimers);


/*
 * Timer Button Injection
 * Adds a small timer button next to timed exercises that opens a floating timer
 */
function wgerInitTimerButtons() {
  // Only run on routine/workout pages
  const path = window.location.pathname;
  if (!path.includes('/routine/') || !path.includes('/view')) {
    return;
  }

  const TIME_UNITS = ['seconds', 'minutes', 'second', 'minute'];
  let buttonsAdded = false;
  let attempts = 0;
  const maxAttempts = 10;

  // Create the floating timer modal (hidden by default)
  createTimerModal();

  // Try to find and add buttons with retry
  const interval = setInterval(function() {
    attempts++;
    if (buttonsAdded || attempts > maxAttempts) {
      clearInterval(interval);
      return;
    }
    buttonsAdded = addTimerButtons();
  }, 1000);

  function createTimerModal() {
    // Check if modal already exists
    if (document.getElementById('wger-timer-modal')) return;

    const modal = document.createElement('div');
    modal.id = 'wger-timer-modal';
    modal.className = 'wger-timer-modal';
    modal.style.cssText = `
      display: none;
      position: fixed;
      top: 50%;
      left: 50%;
      transform: translate(-50%, -50%);
      z-index: 10000;
      background: white;
      border-radius: 16px;
      box-shadow: 0 10px 40px rgba(0,0,0,0.3);
      padding: 20px;
      min-width: 280px;
    `;

    modal.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h5 style="margin: 0; font-weight: 600;">Exercise Timer</h5>
        <button id="wger-timer-close" style="background: none; border: none; font-size: 24px; cursor: pointer; color: #666;">&times;</button>
      </div>
      <div id="wger-timer-container"></div>
    `;

    // Create backdrop
    const backdrop = document.createElement('div');
    backdrop.id = 'wger-timer-backdrop';
    backdrop.style.cssText = `
      display: none;
      position: fixed;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background: rgba(0,0,0,0.5);
      z-index: 9999;
    `;

    document.body.appendChild(backdrop);
    document.body.appendChild(modal);

    // Close handlers
    document.getElementById('wger-timer-close').addEventListener('click', closeTimerModal);
    backdrop.addEventListener('click', closeTimerModal);
  }

  function openTimerModal(duration) {
    const modal = document.getElementById('wger-timer-modal');
    const backdrop = document.getElementById('wger-timer-backdrop');
    const container = document.getElementById('wger-timer-container');

    // Clear previous timer
    container.innerHTML = '';

    // Create new timer
    new CountdownTimer(container, {
      duration: duration,
      onComplete: function() {
        // Flash the modal on completion
        modal.style.animation = 'pulse 0.5s ease-in-out 3';
      }
    });

    modal.style.display = 'block';
    backdrop.style.display = 'block';
  }

  function closeTimerModal() {
    document.getElementById('wger-timer-modal').style.display = 'none';
    document.getElementById('wger-timer-backdrop').style.display = 'none';
  }

  function addTimerButtons() {
    // Find all text nodes containing time patterns
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    const timeNodes = [];
    let node;
    while (node = walker.nextNode()) {
      const text = node.textContent.trim();
      for (const unit of TIME_UNITS) {
        const regex = new RegExp(`^(\\d+)\\s*${unit}$`, 'i');
        const match = text.match(regex);
        if (match) {
          timeNodes.push({
            node: node,
            duration: parseInt(match[1]),
            unit: unit
          });
          break;
        }
      }
    }

    if (timeNodes.length === 0) return false;

    // Add timer button next to each time text
    timeNodes.forEach(item => {
      const parent = item.node.parentElement;
      if (!parent || parent.querySelector('.wger-timer-btn')) return;

      // Convert to seconds
      let durationSeconds = item.duration;
      if (item.unit.startsWith('min')) {
        durationSeconds = item.duration * 60;
      }

      // Create timer button
      const btn = document.createElement('button');
      btn.className = 'wger-timer-btn btn btn-sm btn-outline-primary ms-2';
      btn.innerHTML = '<i class="fa-solid fa-stopwatch"></i>';
      btn.title = 'Start Timer';
      btn.style.cssText = 'padding: 2px 8px; font-size: 12px; vertical-align: middle;';

      btn.addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        openTimerModal(durationSeconds);
      });

      // Insert button after the text
      parent.appendChild(btn);
    });

    return true;
  }
}


// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { CountdownTimer, wgerInitTimers, wgerCreateTimer, wgerInitTimerButtons };
}
