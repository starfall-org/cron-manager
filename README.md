# Cron Manager

A powerful cron job management application built with Svelte and TypeScript on the client side, using Vite as the build tool.

## Overview

This application enables users to create, manage, and schedule automated tasks that run at specified intervals. It's designed for easy deployment through the Genezio platform.

## Project Structure

The project is divided into two main parts:

- **Client**: User interface built with Svelte + TypeScript + Vite
- **Server**: Backend handling cron job management logic using FastAPI

## Installation and Setup

### System Requirements

- Python 3.10+
- Node.js (latest version)
- npm or yarn

### Setup

1. Clone repository:

```bash
git clone https://github.com/starfall-org/cron-manager.git
```

2. Install dependencies:

```bash
# frontend
cd cron-manager
cd client
npm install
# backend
cd ../server
pip install -r requirements.txt
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
- **Backend**: FastAPI
- **Deployment**: Genezio

## Recommended Development Environment

- [VS Code](https://code.visualstudio.com/) with [Svelte](https://marketplace.visualstudio.com/items?itemName=svelte.svelte-vscode) extension

## Technical Notes

- HMR (Hot Module Replacement) enabled for rapid development
- TypeScript configured with `allowJs: true` to support both JavaScript and TypeScript files
- Project structure similar to SvelteKit for future upgrade compatibility

## Contributing

Contributions are welcome. Please create issues or pull requests to contribute to the project.

## Tech Stack

![Svelte](https://raw.githubusercontent.com/sveltejs/branding/master/svelte-logo.svg)
![TypeScript](https://raw.githubusercontent.com/remojansen/logo.ts/master/ts.png)
![Vite](https://vitejs.dev/logo.svg)
![FastAPI](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

## License

![GPL License](https://img.shields.io/badge/License-GPLv3-blue.svg)
