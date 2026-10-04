import { Link, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import Landing from "./pages/Landing";
import Plan from "./pages/Plan";
import Profile from "./pages/Profile";
import Sources from "./pages/Sources";

function NotFound() {
  return (
    <div className="mx-auto max-w-2xl px-4 py-20 text-center">
      <h1 className="text-3xl font-extrabold">This page does not exist</h1>
      <p className="mt-2 text-muted">The link may be old or mistyped.</p>
      <Link to="/" className="mt-6 inline-flex min-h-11 items-center rounded-xl bg-brand px-5 font-bold text-white">
        Go to the home page
      </Link>
    </div>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route index element={<Landing />} />
        <Route path="profile" element={<Profile />} />
        <Route path="plan" element={<Plan />} />
        <Route path="sources" element={<Sources />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
