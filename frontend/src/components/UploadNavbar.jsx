import { Link } from "react-router-dom";

export default function UploadNavbar() {
  return (
    <nav className="navbar1 upload-navbar">
      <h1 className="logo"> EduDub AI</h1>
      <ul className="nav-links">
        <li><Link to="/">⬅️ Back to Home</Link></li>
      </ul>
    </nav>
  );
}
