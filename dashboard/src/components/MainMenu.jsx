import React, {useState} from 'react';
import './MainMenu.css';

export default function MainMenu({items = [], onSelect}){
  const [open, setOpen] = useState(false);

  return (
    <nav className="main-menu">
      <div className="menu-left">
        <button className="hamburger" aria-label="Main menu" aria-expanded={open} onClick={() => setOpen(!open)}>
          <span className="hamburger-box"><span className="hamburger-inner"/></span>
        </button>
        <div className="brand">NetworkBuster</div>
      </div>

      <div className={`menu-items ${open ? 'open' : ''}`} role="menu">
        {items.map(it => (
          <button key={it.key} role="menuitem" className="menu-item" onClick={() => { setOpen(false); onSelect && onSelect(it.key); }}>{it.label}</button>
        ))}
      </div>

      <div className="menu-right" aria-hidden={!open}>
        {/* placeholder for future items */}
      </div>
    </nav>
  )
}
