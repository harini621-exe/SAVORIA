import React from 'react';
import { NavLink, Link } from 'react-router-dom';
import './Navbar.css';

export default function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          <span className="navbar-brand-icon">S</span>
          <span className="navbar-brand-name">SAVORIA</span>
        </Link>

        <nav className="navbar-nav" aria-label="Main navigation">
          <NavLink to="/" end className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Home
          </NavLink>
          <NavLink to="/create" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Create Recipe
          </NavLink>
          <NavLink to="/saved" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            Saved
          </NavLink>
          <NavLink to="/about" className={({ isActive }) => isActive ? 'nav-link active' : 'nav-link'}>
            About
          </NavLink>
        </nav>

        <Link to="/create" className="btn btn-primary btn-sm navbar-cta">
          Get Started
        </Link>
      </div>
    </header>
  );
}
