# Matrix Layout with RedPoint - Technical Specification

## Overview

The Matrix Layout is a flexible 2×2 grid system with a draggable intersection point (RedPoint) that allows dynamic resizing of all four panels simultaneously. This document describes the functionality, behavior, and implementation details of this component, including testing procedures.

## Components

### 1. Matrix Container
- A 2×2 grid layout container
- Configurable using CSS Grid with fractional units (`fr`)
- Maintains relative sizing between panels
- Responsive to window resizing

### 2. RedPoint (Intersection Point)
- A draggable control point positioned at the intersection of the four panels
- Visually represented as a red circular handle
- Displays current position coordinates on hover/drag
- Limited to movement within 20%-80% range in both X and Y directions

### 3. Matrix Panels
- Four panels arranged in a 2×2 grid
- Each panel can be individually expanded to dominant size (80% of available space) but not 
- Panels maintain content during resizing operations
- Support for different content types based on application mode

## Functionality

### 1. RedPoint Dragging
- **Behavior**: User can drag the RedPoint to resize all four panels simultaneously
- **Constraints**: Movement limited to 20%-80% range from edges
- **Visual Feedback**: Position indicator shows exact percentage coordinates
- **Implementation**: Uses mouse events (mousedown, mousemove, mouseup) with position calculations

### 2. Panel Expansion
- **Behavior**: Clicking on a panel expands it to 80% of available space
- **Toggle**: Clicking an already expanded panel resets the layout to 50/50 split
- **RedPoint Position**: Automatically updates to reflect the new panel proportions
- **Implementation**: Panel click events with predefined grid templates

### 3. Layout Persistence
- **State Management**: Current layout configuration is stored in application state
- **Reset Capability**: Layout can be reset to default 50/50 configuration
- **Mode Switching**: Layout persists when switching between application modes

## Technical Implementation

### CSS Grid Configuration
```css
.matrix-container {
    display: grid;
    grid-template-columns: 50fr 50fr;  /* Default 50/50 split */
    grid-template-rows: 50fr 50fr;     /* Default 50/50 split */
    gap: 10px;
    position: relative;
    overflow: hidden;
}
```

### RedPoint Positioning
The RedPoint position is calculated as a percentage of the container dimensions and applied using CSS:
```javascript
// Example: Setting RedPoint at 60% horizontally, 40% vertically
intersectionPoint.style.left = '60%';
intersectionPoint.style.top = '40%';
```

### Grid Template Updates
When the RedPoint is moved, the grid template is updated using fractional units:
```javascript
// Example: RedPoint at 60% horizontally, 40% vertically
matrixContainer.style.gridTemplateColumns = '60fr 40fr';
matrixContainer.style.gridTemplateRows = '40fr 60fr';
```

### Panel Expansion Logic
When a panel is clicked, the grid template is updated based on which panel was selected:
```javascript
// Example: Expanding top-left panel
matrixContainer.style.gridTemplateColumns = '80fr 20fr';
matrixContainer.style.gridTemplateRows = '80fr 20fr';
```

## Interaction Patterns

### 1. Direct RedPoint Manipulation
1. User hovers over RedPoint (cursor changes to "move")
2. User clicks and holds RedPoint
3. User drags to desired position (within 20%-80% constraints)
4. Position indicator shows current coordinates
5. User releases mouse button to set new position
6. All four panels resize according to new grid template

### 2. Panel Click Expansion
1. User clicks on a panel (not on a control or interactive element)
2. Panel expands to 80% of available space in both directions
3. RedPoint moves to corresponding position
4. Clicking the expanded panel again resets to 50/50 layout

### 3. Panel Header Interaction
1. User clicks on panel header
2. Same behavior as clicking the panel itself
3. Panel expands or resets based on current state

## Visual Design

### RedPoint Styling
- Red circular handle (20px diameter)
- White border with subtle shadow
- Scale effect on hover (120%)
- Position indicator appears on hover/drag

### Panel Styling
- Light background with subtle shadow
- Border highlight based on current application mode
- Enhanced shadow effect for expanded panel
- Smooth transitions for all size changes

## Edge Cases and Error Handling

### Window Resizing
- RedPoint maintains its percentage position when window is resized
- Grid layout adapts proportionally to available space

### Panel Content Overflow
- Panels handle content overflow with scrolling when necessary
- Content maintains visibility during resize operations

### Touch Device Support
- RedPoint supports touch events for mobile/tablet use
- Larger touch target for better mobile usability

## Usage Examples

### Default Layout (50/50 split)
- All panels have equal size
- RedPoint positioned at center (50%, 50%)

### Content Focus Layout
- One panel expanded to 80% in both directions
- Other panels reduced to 20% of available space
- RedPoint positioned at intersection (e.g., 80%, 80% for top-left panel focus)

### Horizontal Split Emphasis
- RedPoint positioned at (50%, 30%)
- More vertical space allocated to bottom panels

### Vertical Split Emphasis
- RedPoint positioned at (30%, 50%)
- More horizontal space allocated to right panels

## Implementation Notes

1. The RedPoint position is tracked in percentage values for responsive behavior
2. Grid templates use fractional units (`fr`) rather than percentages for better layout control
3. A MutationObserver watches for style changes to keep RedPoint position in sync
4. Window resize events trigger position recalculation to maintain layout integrity

## Testing Framework

### Automated Browser Testing

The Matrix Layout functionality is tested using Playwright, a modern browser automation framework that supports multiple browsers. The tests verify that all aspects of the Matrix Layout function correctly across different browsers and screen sizes.

### Test Cases

1. **Matrix Mode Activation**
   - Test that clicking the "Tryb Matrix" button activates matrix mode
   - Verify that the RedPoint appears at the center (50%, 50%)
   - Confirm that the grid layout is initially set to equal proportions

2. **Panel Expansion Tests**
   - Test clicking on each panel individually
   - Verify that the clicked panel expands to 80% of available space
   - Confirm that the RedPoint moves to the correct position for each panel:
     - Top-Left (`media-panel`): RedPoint at (80%, 80%)
     - Top-Right (`edit-panel`): RedPoint at (20%, 80%)
     - Bottom-Left (`preview-panel`): RedPoint at (80%, 20%)
     - Bottom-Right (`communication-panel`): RedPoint at (20%, 20%)

3. **RedPoint Dragging Tests**
   - Test dragging the RedPoint to various positions
   - Verify that the grid layout updates in real-time
   - Confirm that the RedPoint cannot be dragged beyond the 20%-80% constraints
   - Test that the position indicator displays the correct coordinates

4. **Reset Functionality Tests**
   - Test that clicking an already expanded panel resets the layout
   - Verify that toggling matrix mode off and on resets the layout
   - Confirm that the RedPoint returns to the center position (50%, 50%)

5. **Edge Case Tests**
   - Test behavior when rapidly clicking multiple panels
   - Verify correct behavior when dragging beyond container boundaries
   - Test interaction with other UI elements during matrix mode

### Running the Tests

The automated tests can be run using the following command:

```bash
npm test matrix-layout
```

This will execute all test cases across Chrome, Firefox, and Safari (when available). Test results are output to the console and a detailed HTML report is generated in the `test-results` directory.

### Manual Testing Checklist

In addition to automated tests, manual testing should verify:

1. ✓ Matrix mode can be toggled on and off
2. ✓ RedPoint is visible and draggable
3. ✓ Clicking each panel expands it correctly
4. ✓ RedPoint moves to the correct position for each panel
5. ✓ Dragging the RedPoint resizes all panels simultaneously
6. ✓ Position indicator shows correct coordinates
7. ✓ Layout resets correctly when clicking an expanded panel
8. ✓ All interactions work smoothly without visual glitches

---

## Appendix: Event Flow Diagram

```
User Interaction → Event Handler → Position Calculation → Grid Template Update → Visual Feedback
```

## Appendix: Panel Identification

1. Top-Left: `media-panel`
2. Top-Right: `edit-panel`
3. Bottom-Left: `preview-panel`
4. Bottom-Right: `communication-panel`
