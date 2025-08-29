import Navbar from "../components/Navbar.jsx";
import Hero from "../components/Hero.jsx";
import Features from "../components/Features.jsx";
import Workflow from "../components/Workflow.jsx";
import Footer from "../components/Footer.jsx";

export default function Home() {
  return (
    <div>
      <Navbar />
      <Hero />
      <Features />
      <Workflow />
      <Footer />
    </div>
  );
}
