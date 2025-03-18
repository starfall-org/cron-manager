# Cron Manager

A powerful cron job management application built with Svelte and TypeScript on the client side, using Vite as the build tool.

## Overview

This application enables users to create, manage, and schedule automated tasks that run at specified intervals. It's designed for easy deployment through the Genezio platform.

## Project Structure

The project is divided into two main parts:

- **Client**: User interface built with Svelte + TypeScript + Vite
- **Server**: Backend handling cron job management logic

## Installation and Setup

### System Requirements
- Node.js (latest version)
- npm or yarn

### Setup
1. Clone repository:
```bash
git clone https://github.com/your-username/cron-manager.git
```

2. Install dependencies:
```bash
cd cron-manager
npm install
```

3. Run in development mode:
```bash
npm run dev
```

## Deployment

Deploy this application to Genezio with one click:

[![Genezio Deploy](https://raw.githubusercontent.com/Genez-io/graphics/main/svg/deploy-button.svg)](https://app.genez.io/start/deploy?repository=https://github.com/starfall-app/cron-manager)

## Tech Stack

- **Frontend**: Svelte, TypeScript, Vite
- **Backend**: Node.js
- **Deployment**: Genezio

## Recommended Development Environment

- [VS Code](https://code.visualstudio.com/) with [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode) extension

## Technical Notes

- HMR (Hot Module Replacement) enabled for rapid development
- TypeScript configured with `allowJs: true` to support both JavaScript and TypeScript files
- Project structure similar to SvelteKit for future upgrade compatibility

## Contributing

Contributions are welcome. Please create issues or pull requests to contribute to the project.

## License

[MIT License](LICENSE)