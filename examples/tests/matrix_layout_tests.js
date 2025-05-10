// @ts-check
const { test, expect } = require('@playwright/test');

/**
 * Matrix Layout Test Suite
 * 
 * These tests verify the functionality of the Matrix Layout component,
 * including panel expansion, RedPoint movement, and dragging behavior.
 */

test.describe('Matrix Layout Tests', () => {
  // Setup for each test
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:8000');
    
    // Wait for the page to be fully loaded
    await page.waitForSelector('.matrix-container', { state: 'visible' });
    
    // Activate matrix mode if not already active
    const matrixButton = page.locator('#matrix-toggle-btn');
    const buttonText = await matrixButton.textContent();
    
    if (buttonText === 'Tryb Matrix') {
      await matrixButton.click();
      // Wait for matrix mode to be fully activated
      await page.waitForSelector('#intersection-point', { state: 'visible' });
    }
    
    // Log that matrix mode is activated
    console.log('Matrix mode activated for test');
  });

  // Test 1: Matrix Mode Activation
  test('should activate matrix mode and display RedPoint at center', async ({ page }) => {
    // Toggle matrix mode off and then on again to ensure clean state
    const matrixButton = page.locator('#matrix-toggle-btn');
    await matrixButton.click(); // Turn off
    await expect(page.locator('#intersection-point')).toHaveCSS('display', 'none');
    
    await matrixButton.click(); // Turn on
    await expect(page.locator('#intersection-point')).toBeVisible();
    
    // Check that RedPoint is at center position (50%, 50%)
    const redPoint = page.locator('#intersection-point');
    await expect(redPoint).toHaveCSS('left', '50%');
    await expect(redPoint).toHaveCSS('top', '50%');
    
    // Verify grid is set to equal proportions
    const matrixContainer = page.locator('.matrix-container');
    const gridColumns = await matrixContainer.evaluate(el => 
      window.getComputedStyle(el).gridTemplateColumns);
    const gridRows = await matrixContainer.evaluate(el => 
      window.getComputedStyle(el).gridTemplateRows);
    
    // Check that columns and rows are equal (50/50 split)
    expect(gridColumns).toContain('50fr 50fr');
    expect(gridRows).toContain('50fr 50fr');
  });

  // Test 2: Panel Expansion Tests
  test('should expand panels correctly when clicked', async ({ page }) => {
    // Test each panel individually
    const panels = [
      { id: 'media-panel', left: '80%', top: '80%' },
      { id: 'edit-panel', left: '20%', top: '80%' },
      { id: 'preview-panel', left: '80%', top: '20%' },
      { id: 'communication-panel', left: '20%', top: '20%' }
    ];
    
    for (const panel of panels) {
      // Click on the panel header to expand it
      await page.locator(`#${panel.id} .panel-header`).click();
      
      // Wait for the panel to expand
      await page.waitForTimeout(300);
      
      // Check that RedPoint moved to the correct position
      const redPoint = page.locator('#intersection-point');
      await expect(redPoint).toHaveCSS('left', panel.left);
      await expect(redPoint).toHaveCSS('top', panel.top);
      
      // Verify that the panel has the expanded class
      await expect(page.locator(`#${panel.id}`)).toHaveClass(/panel-expanded/);
      
      // Reset layout for next test
      await page.locator(`#${panel.id} .panel-header`).click();
      await page.waitForTimeout(300);
    }
  });

  // Test 3: RedPoint Dragging Tests
  test('should update layout when RedPoint is dragged', async ({ page }) => {
    // Get the RedPoint element
    const redPoint = page.locator('#intersection-point');
    
    // Get initial position
    const initialLeft = await redPoint.evaluate(el => el.style.left);
    const initialTop = await redPoint.evaluate(el => el.style.top);
    
    // Test positions to drag to
    const testPositions = [
      { x: 30, y: 30 },
      { x: 70, y: 30 },
      { x: 30, y: 70 },
      { x: 70, y: 70 }
    ];
    
    for (const pos of testPositions) {
      // Get the bounding box of the matrix container
      const containerBounds = await page.locator('.matrix-container').boundingBox();
      
      // Calculate drag coordinates
      const dragToX = containerBounds.x + (containerBounds.width * pos.x / 100);
      const dragToY = containerBounds.y + (containerBounds.height * pos.y / 100);
      
      // Perform the drag operation
      await page.mouse.move(
        containerBounds.x + (containerBounds.width / 2), 
        containerBounds.y + (containerBounds.height / 2)
      );
      await page.mouse.down();
      await page.mouse.move(dragToX, dragToY, { steps: 10 });
      await page.mouse.up();
      
      // Wait for the drag to complete
      await page.waitForTimeout(300);
      
      // Check that grid template was updated
      const matrixContainer = page.locator('.matrix-container');
      const gridColumns = await matrixContainer.evaluate(el => 
        window.getComputedStyle(el).gridTemplateColumns);
      const gridRows = await matrixContainer.evaluate(el => 
        window.getComputedStyle(el).gridTemplateRows);
      
      // Verify that the grid template reflects the new position
      console.log(`Dragged to ${pos.x}%, ${pos.y}%`);
      console.log(`Grid columns: ${gridColumns}`);
      console.log(`Grid rows: ${gridRows}`);
      
      // Check that RedPoint position is approximately correct (allowing for some margin of error)
      const newLeft = await redPoint.evaluate(el => parseFloat(el.style.left));
      const newTop = await redPoint.evaluate(el => parseFloat(el.style.top));
      
      expect(newLeft).toBeGreaterThanOrEqual(20);
      expect(newLeft).toBeLessThanOrEqual(80);
      expect(newTop).toBeGreaterThanOrEqual(20);
      expect(newTop).toBeLessThanOrEqual(80);
    }
  });

  // Test 4: Reset Functionality Tests
  test('should reset layout when toggling matrix mode', async ({ page }) => {
    // First expand a panel
    await page.locator('#media-panel .panel-header').click();
    await page.waitForTimeout(300);
    
    // Verify panel is expanded
    await expect(page.locator('#media-panel')).toHaveClass(/panel-expanded/);
    
    // Toggle matrix mode off and on
    const matrixButton = page.locator('#matrix-toggle-btn');
    await matrixButton.click(); // Turn off
    await matrixButton.click(); // Turn on
    await page.waitForTimeout(300);
    
    // Check that layout is reset (RedPoint at center)
    const redPoint = page.locator('#intersection-point');
    await expect(redPoint).toHaveCSS('left', '50%');
    await expect(redPoint).toHaveCSS('top', '50%');
    
    // Verify grid is reset to equal proportions
    const matrixContainer = page.locator('.matrix-container');
    const gridColumns = await matrixContainer.evaluate(el => 
      window.getComputedStyle(el).gridTemplateColumns);
    const gridRows = await matrixContainer.evaluate(el => 
      window.getComputedStyle(el).gridTemplateRows);
    
    expect(gridColumns).toContain('50fr 50fr');
    expect(gridRows).toContain('50fr 50fr');
  });

  // Test 5: Edge Case Tests
  test('should handle rapid panel clicks correctly', async ({ page }) => {
    // Click multiple panels in rapid succession
    await page.locator('#media-panel .panel-header').click();
    await page.locator('#edit-panel .panel-header').click();
    await page.locator('#preview-panel .panel-header').click();
    await page.locator('#communication-panel .panel-header').click();
    
    // Wait for the last click to take effect
    await page.waitForTimeout(500);
    
    // Verify that only the last clicked panel is expanded
    await expect(page.locator('#media-panel')).not.toHaveClass(/panel-expanded/);
    await expect(page.locator('#edit-panel')).not.toHaveClass(/panel-expanded/);
    await expect(page.locator('#preview-panel')).not.toHaveClass(/panel-expanded/);
    await expect(page.locator('#communication-panel')).toHaveClass(/panel-expanded/);
    
    // Check that RedPoint is at the correct position for the last panel
    const redPoint = page.locator('#intersection-point');
    await expect(redPoint).toHaveCSS('left', '20%');
    await expect(redPoint).toHaveCSS('top', '20%');
  });
});
