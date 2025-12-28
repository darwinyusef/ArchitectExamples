# Learn React Basics

## Overview
React is a JavaScript library for building user interfaces. This goal will guide you through the fundamentals.

## Tutorial Video
[youtube](dQw4w9WgXcQ)

## React Component Architecture

![React Component Tree](https://react.dev/images/docs/diagram-tree.svg)

### Key Concepts

#### Components
Components are the building blocks of React applications. They can be:
- **Functional Components**: Modern approach using hooks
- **Class Components**: Traditional approach (legacy)

Example:
```jsx
function Welcome(props) {
  return <h1>Hello, {props.name}</h1>;
}
```

#### JSX
JavaScript XML - a syntax extension that looks like HTML:
```jsx
const element = <h1>Hello, world!</h1>;
```

#### Props
Data passed from parent to child components:
```jsx
<Welcome name="Sara" />
```

#### State
Component-specific data that changes over time:
```jsx
const [count, setCount] = useState(0);
```

## Learning Path

### Step 1: Setup
- Install Node.js and npm
- Create React app: `npx create-react-app my-app`

### Step 2: First Component
- Create a functional component
- Return JSX
- See it render

### Step 3: Add State
- Import `useState`
- Declare state variable
- Update state with setter

### Step 4: Event Handling
- Add onClick handler
- Update state on click
- See component re-render

## Resources

- [Official React Docs](https://react.dev)
- [React Hooks Documentation](https://react.dev/reference/react)
- [Thinking in React](https://react.dev/learn/thinking-in-react)

## Expected Outcomes

By the end of this goal, you should be able to:
1. ✅ Create functional components
2. ✅ Use useState hook
3. ✅ Handle events (onClick, onChange)
4. ✅ Pass props between components
5. ✅ Understand component lifecycle

## Common Mistakes to Avoid

1. ❌ Mutating state directly
2. ❌ Not using keys in lists
3. ❌ Forgetting to bind event handlers
4. ❌ Using wrong component hierarchy

## Next Steps

After mastering basics:
- Learn useEffect for side effects
- Explore React Router for navigation
- Study state management with Context API
- Build a real project!
