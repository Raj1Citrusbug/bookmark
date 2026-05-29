/** @type {import('tailwindcss').Config} */
export default {
  darkMode: ['class'],
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
  	extend: {
  		borderRadius: {
  			lg: 'var(--radius)',
  			md: 'calc(var(--radius) - 2px)',
  			sm: 'calc(var(--radius) - 4px)'
  		},
      fontFamily: {
          sans: ['"Inter"', '"Noto Sans"', 'sans-serif'],
          display: ['"Outfit"', '"Euro Sans"', 'sans-serif'],
          accent: ['"Playfair Display"', '"Meno Banner"', 'serif'],
      },
  		colors: {
        'eerie-black': 'hsl(var(--eerie-black))',
        'gold-yellow': 'hsl(var(--gold-yellow))',
        'ivory': 'hsl(var(--ivory))',
        'space': 'hsl(var(--space))',
        'spanish-gray': 'hsl(var(--spanish-gray))',

  			background: 'hsl(var(--background))',
  			foreground: 'hsl(var(--foreground))',
  			card: {
  				DEFAULT: 'hsl(var(--card))',
  				foreground: 'hsl(var(--card-foreground))'
  			},
  			popover: {
  				DEFAULT: 'hsl(var(--popover))',
  				foreground: 'hsl(var(--popover-foreground))'
  			},
  			primary: {
  				DEFAULT: 'hsl(var(--primary))',
  				foreground: 'hsl(var(--primary-foreground))'
  			},
  			secondary: {
  				DEFAULT: 'hsl(var(--secondary))',
  				foreground: 'hsl(var(--secondary-foreground))'
  			},
  			muted: {
  				DEFAULT: 'hsl(var(--muted))',
  				foreground: 'hsl(var(--muted-foreground))'
  			},
  			accent: {
  				DEFAULT: 'hsl(var(--accent))',
  				foreground: 'hsl(var(--accent-foreground))'
  			},
  			destructive: {
  				DEFAULT: 'hsl(var(--destructive))',
  				foreground: 'hsl(var(--destructive-foreground))'
  			},
  			border: 'hsl(var(--border))',
  			'sidebar-border': 'rgba(255, 255, 255, 0.1)',
  			input: 'hsl(var(--input))',
  			ring: 'hsl(var(--ring))',
  		}
  	}
  },
  plugins: [require("tailwindcss-animate")],
}
