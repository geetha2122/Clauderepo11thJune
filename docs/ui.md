# UI Component Standards

## Important Rules

**ABSOLUTELY NO custom components should be created.** This project uses only shadcn UI components and Tailwind CSS.

## Allowed Components

- shadcn UI Button
- shadcn UI Input
- shadcn UI Calendar
- shadcn UI Card
- shadcn UI Badge
- shadcn UI Dialog
- shadcn UI Dropdown Menu
- shadcn UI Select
- And all other shadcn UI components

## Date Formatting

All dates must be formatted using date-fns library with ordinal suffixes:
- "1st Sept 2026"
- "2nd Aug 2026"
- "3rd July 2026"
- "4th June 2026"

Example:
```javascript
import { format } from 'date-fns';

function formatDateWithOrdinal(date) {
    const formatter = new Intl.DateTimeFormat('en-US', { 
        day: 'numeric', 
        month: 'long', 
        year: 'numeric' 
    });
    const parts = formatter.formatToParts(date);
    
    const day = parseInt(parts.find(p => p.type === 'day').value);
    const month = parts.find(p => p.type === 'month').value;
    const year = parts.find(p => p.type === 'year').value;
    
    const ordinal = getOrdinalSuffix(day);
    return `${day}${ordinal} ${month} ${year}`;
}
```

## Styling

Use Tailwind CSS utility classes for all styling. Never write custom CSS or create new stylesheets.
