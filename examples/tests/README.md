# Matrix Layout Testing

This directory contains automated browser tests for the Matrix Layout functionality using Playwright.

## Overview

The tests verify that all aspects of the Matrix Layout function correctly, including:

- Matrix mode activation/deactivation
- Panel expansion when clicked
- RedPoint movement to correct positions
- RedPoint dragging functionality
- Layout reset functionality
- Edge case handling

## Setup

To run the tests, you'll need Node.js and npm installed. Then install the dependencies:

```bash
cd /path/to/devopy/examples/tests
npm install
npx playwright install
```

## Running Tests

### Run all tests

```bash
npm test
```

### Run only Matrix Layout tests

```bash
npm run test:matrix
```

### Run tests in specific browsers

```bash
npm run test:chrome
npm run test:firefox
npm run test:safari
```

### Debug tests

To run tests in debug mode with UI:

```bash
npm run test:debug
```

### View test report

After running tests, you can view the HTML report:

```bash
npm run report
```

## Test Structure

The tests are organized as follows:

1. **Matrix Mode Activation Test**: Verifies that matrix mode can be toggled on/off and that the RedPoint appears at the center (50%, 50%).

2. **Panel Expansion Tests**: Tests clicking on each panel and verifies that:
   - The clicked panel expands to 80% of available space
   - The RedPoint moves to the correct position for each panel

3. **RedPoint Dragging Tests**: Tests dragging the RedPoint to various positions and verifies that:
   - The grid layout updates in real-time
   - The RedPoint cannot be dragged beyond the 20%-80% constraints

4. **Reset Functionality Tests**: Verifies that the layout resets correctly when:
   - Clicking an already expanded panel
   - Toggling matrix mode off and on

5. **Edge Case Tests**: Tests behavior in edge cases such as:
   - Rapidly clicking multiple panels
   - Dragging beyond container boundaries

## Manual Testing Checklist

In addition to automated tests, use this checklist for manual testing:

- [ ] Matrix mode can be toggled on and off
- [ ] RedPoint is visible and draggable
- [ ] Clicking each panel expands it correctly
- [ ] RedPoint moves to the correct position for each panel
- [ ] Dragging the RedPoint resizes all panels simultaneously
- [ ] Position indicator shows correct coordinates
- [ ] Layout resets correctly when clicking an expanded panel
- [ ] All interactions work smoothly without visual glitches
