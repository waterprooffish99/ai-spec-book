import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

// --- START: Defined Configuration Variables ---
// Your GitHub Information (SET FOR YOU)
const organizationName = 'waterprooffish99';
const projectName = 'ai-spec-book'; 
// --- END: Defined Configuration Variables ---


const config: Config = {
  // --- SITE METADATA & DEPLOYMENT CONFIGURATION ---
  title: 'The Spec-Driven AI Engineer',
  tagline: 'Mastering Agentic Workflows for Faculty and Senior Students',
  favicon: 'img/favicon.ico',

  // The root URL for your GitHub Pages site (no trailing slash)
  url: `https://${organizationName}.github.io`, 
  // The path to your repository (must start and end with a slash for GH Pages)
  baseUrl: `/${projectName}/`, 

  // GitHub pages deployment config.
  organizationName: organizationName, 
  projectName: projectName, 
  // Safety measure: warn on broken links during hackathon, don't stop the build.
  onBrokenLinks: 'warn', 
  onBrokenMarkdownLinks: 'warn',

  trailingSlash: false, 

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  future: {
    v4: true, 
  },
  
  // --- PRESETS (Theme, Docs, Blog) ---
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          // CRITICAL CHANGE: This makes your Docs the homepage!
          routeBasePath: '/', 
          // Link to edit pages on GitHub
          editUrl: `https://github.com/${organizationName}/${projectName}/tree/main/`, 
        },
        blog: {
          showReadingTime: true,
          // Link to edit blog posts on GitHub
          editUrl: `https://github.com/${organizationName}/${projectName}/tree/main/`,
        },
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  // --- THEME CONFIGURATION (Navbar and Footer) ---
  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'AI-Driven Engineer',
      logo: {
        alt: 'AI-Driven Engineer Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'The Book',
        },
        {to: '/blog', label: 'Blog', position: 'left'}, 
        {
          href: `https://github.com/${organizationName}/${projectName}`,
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'The Book',
              to: '/',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Spec-Driven AI Hackathon Project. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;