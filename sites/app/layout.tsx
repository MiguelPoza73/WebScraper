import type { Metadata } from 'next';
import './globals.css';
export const metadata:Metadata={title:'Web a Excel · Extrae, revisa y descarga',description:'Extrae tablas HTML y elementos CSS de páginas públicas y descarga tus datos en Excel o CSV.',icons:{icon:'/favicon.svg'}};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="es"><body>{children}</body></html>}
