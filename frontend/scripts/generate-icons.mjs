import sharp from 'sharp';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
const publicDir = join(__dirname, '..', 'public');

// Kolosal brand color (dark)
const backgroundColor = '#0D0E0F';

// SVG with white logo on dark background
const createIconSvg = (size) => `
<svg width="${size}" height="${size}" viewBox="0 0 ${size} ${size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="${size}" height="${size}" fill="${backgroundColor}" rx="${size * 0.15}"/>
  <g transform="translate(${size * 0.15}, ${size * 0.18}) scale(${size / 35})">
    <path fill-rule="evenodd" clip-rule="evenodd" d="M15.6709 11.6602C15.7437 11.7823 15.7894 11.923 15.7894 12.0755C15.7894 12.2554 15.7279 12.4198 15.6292 12.5547L27.055 23.9805L27.3337 24.2604H8.37793L0.666992 16.5495V7.71094L8.37793 0H27.3337L15.6709 11.6602ZM11.2464 16.0846C11.3325 16.2139 11.3831 16.3695 11.3831 16.5365C11.383 16.7338 11.3097 16.9123 11.193 17.0534L18.0732 23.9336H24.9834C24.9899 23.7379 25.0307 23.5445 25.1058 23.3633C25.1865 23.1685 25.304 22.9911 25.4521 22.8411L15.387 12.7747C15.2653 12.847 15.1249 12.8919 14.973 12.8919C14.8201 12.8919 14.6786 12.8466 14.5563 12.7734L11.2464 16.0846ZM6.66699 12.1302L10.0485 15.9089C10.1896 15.792 10.3693 15.7201 10.5667 15.7201C10.7321 15.7201 10.8861 15.7696 11.0146 15.8542L14.3141 12.5547C14.216 12.42 14.1566 12.2549 14.1566 12.0755C14.1566 11.9235 14.2 11.782 14.2725 11.6602L11.124 8.51172C10.9952 8.59695 10.8421 8.64839 10.6761 8.64844C10.4223 8.64844 10.1981 8.53067 10.0485 8.34896L6.66699 12.1302ZM11.1904 7.20573C11.3726 7.35537 11.4912 7.57919 11.4912 7.83333C11.4911 7.99914 11.4409 8.15253 11.3558 8.28125L14.4925 11.418C14.6274 11.3192 14.793 11.2591 14.973 11.2591C15.1526 11.2591 15.3174 11.3196 15.4521 11.418L25.4521 1.41797C25.3041 1.26803 25.1864 1.09054 25.1058 0.895833C25.0309 0.714898 24.99 0.522236 24.9834 0.326823H18.0719L11.1904 7.20573Z" fill="white"/>
  </g>
</svg>
`;

async function generateIcons() {
  console.log('Generating PWA icons...');

  // Generate 192x192 icon
  await sharp(Buffer.from(createIconSvg(192)))
    .png()
    .toFile(join(publicDir, 'kolosal-192.png'));
  console.log('Created kolosal-192.png');

  // Generate 512x512 icon
  await sharp(Buffer.from(createIconSvg(512)))
    .png()
    .toFile(join(publicDir, 'kolosal-512.png'));
  console.log('Created kolosal-512.png');

  // Generate apple-touch-icon (180x180)
  await sharp(Buffer.from(createIconSvg(180)))
    .png()
    .toFile(join(publicDir, 'apple-touch-icon.png'));
  console.log('Created apple-touch-icon.png');

  // Generate favicon (32x32)
  await sharp(Buffer.from(createIconSvg(32)))
    .png()
    .toFile(join(publicDir, 'favicon-32x32.png'));
  console.log('Created favicon-32x32.png');

  // Generate favicon (16x16)
  await sharp(Buffer.from(createIconSvg(16)))
    .png()
    .toFile(join(publicDir, 'favicon-16x16.png'));
  console.log('Created favicon-16x16.png');

  console.log('All icons generated successfully!');
}

generateIcons().catch(console.error);
