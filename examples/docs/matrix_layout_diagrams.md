# Matrix Layout Diagrams

## Default Layout (50/50 Split)

```
┌─────────────┬─────────────┐
│             │             │
│  Panel 1    │  Panel 2    │
│  (Media)    │  (Edit)     │
│             │             │
├──────●──────┼─────────────┤
│             │             │
│  Panel 3    │  Panel 4    │
│  (Preview)  │  (Comm.)    │
│             │             │
└─────────────┴─────────────┘
     RedPoint at (50%, 50%)
```

## Panel 1 Expanded (Top-Left Focus)

```
┌───────────────────┬─────┐
│                   │     │
│                   │     │
│                   │     │
│     Panel 1       │  P2 │
│     (Media)       │     │
│                   │     │
│                   │     │
├───────────●───────┼─────┤
│                   │     │
│     Panel 3       │  P4 │
│                   │     │
└───────────────────┴─────┘
     RedPoint at (80%, 80%)
```

## Panel 2 Expanded (Top-Right Focus)

```
┌─────┬───────────────────┐
│     │                   │
│     │                   │
│     │                   │
│  P1 │     Panel 2       │
│     │     (Edit)        │
│     │                   │
│     │                   │
├─────┼───────────●───────┤
│     │                   │
│  P3 │     Panel 4       │
│     │                   │
└─────┴───────────────────┘
     RedPoint at (20%, 80%)
```

## Panel 3 Expanded (Bottom-Left Focus)

```
┌───────────────────┬─────┐
│                   │     │
│     Panel 1       │  P2 │
│                   │     │
├───────────●───────┼─────┤
│                   │     │
│                   │     │
│                   │     │
│     Panel 3       │  P4 │
│     (Preview)     │     │
│                   │     │
│                   │     │
└───────────────────┴─────┘
     RedPoint at (80%, 20%)
```

## Panel 4 Expanded (Bottom-Right Focus)

```
┌─────┬───────────────────┐
│     │                   │
│  P1 │     Panel 2       │
│     │                   │
├─────┼───────────●───────┤
│     │                   │
│     │                   │
│     │                   │
│  P3 │     Panel 4       │
│     │     (Comm.)       │
│     │                   │
│     │                   │
└─────┴───────────────────┘
     RedPoint at (20%, 20%)
```

## Custom Layout (Horizontal Emphasis)

```
┌─────────────┬─────────────┐
│             │             │
│  Panel 1    │  Panel 2    │
│             │             │
├──────●──────┼─────────────┤
│             │             │
│             │             │
│  Panel 3    │  Panel 4    │
│             │             │
│             │             │
└─────────────┴─────────────┘
     RedPoint at (50%, 30%)
```

## Custom Layout (Vertical Emphasis)

```
┌────────┬──────────────────┐
│        │                  │
│        │                  │
│ Panel 1│     Panel 2      │
│        │                  │
│        │                  │
├────────┼──────●───────────┤
│        │                  │
│        │                  │
│ Panel 3│     Panel 4      │
│        │                  │
│        │                  │
└────────┴──────────────────┘
     RedPoint at (30%, 50%)
```

## RedPoint Movement Constraints

```
┌─────────────────────────────┐
│                             │
│     ┌─────────────────┐     │
│     │                 │     │
│     │  Valid Movement │     │
│     │      Range      │     │
│     │                 │     │
│     │                 │     │
│     └─────────────────┘     │
│                             │
└─────────────────────────────┘
   20% ←    60%    → 80%
```

## RedPoint Interaction Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Mouse Down on │     │ Mouse Move    │     │ Mouse Up      │
│ RedPoint      │ ──► │ (Drag)        │ ──► │ (Release)     │
└───────────────┘     └───────────────┘     └───────────────┘
                             │                      │
                             ▼                      ▼
                      ┌───────────────┐     ┌───────────────┐
                      │ Calculate New │     │ Update Grid   │
                      │ Position      │     │ Template      │
                      └───────────────┘     └───────────────┘
                             │                      │
                             ▼                      ▼
                      ┌───────────────┐     ┌───────────────┐
                      │ Update Visual │     │ Finalize      │
                      │ Position      │     │ Layout        │
                      └───────────────┘     └───────────────┘
```

## Panel Click Interaction Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│ Click on      │     │ Check Current │     │ Expand Panel  │
│ Panel         │ ──► │ State         │ ──► │ or Reset      │
└───────────────┘     └───────────────┘     └───────────────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │ Update Grid   │
                                            │ Template      │
                                            └───────────────┘
                                                    │
                                                    ▼
                                            ┌───────────────┐
                                            │ Move RedPoint │
                                            │ to Match      │
                                            └───────────────┘
```
