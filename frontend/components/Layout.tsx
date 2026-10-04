import { useEffect } from "react";
import { Link, NavLink, Outlet, useLocation } from "react-router-dom";

const NAV = [
  { to: "/", label: "Home" },
  { to: "/#how", label: "How it works" },
  { to: "/#preview", label: "Universities" },
  { to: "/sources", label: "Sources" },
];

/** Scroll to the #section in the URL, or to the top on a new page. */
function useScrollToHash() {
  const { pathname, hash } = useLocation();
  useEffect(() => {
    if (hash) {
      document.getElementById(hash.slice(1))?.scrollIntoView();
    } else {
      window.scrollTo(0, 0);
    }
  }, [pathname, hash]);
}

export function Layout() {
  useScrollToHash();
  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-20 border-b border-line bg-white/90 backdrop-blur">
        <div className="mx-auto flex h-16 max-w-5xl items-center justify-between gap-4 px-4">
          <Link to="/" className="flex items-center gap-2 text-lg font-extrabold">
            <span aria-hidden className="grid h-8 w-8 place-items-center rounded-lg bg-brand text-white">
              R
            </span>
            Rehnuma
          </Link>
          <nav aria-label="Main" className="hidden items-center gap-6 text-[15px] font-medium text-muted md:flex">
            {NAV.map((item) =>
              item.to.includes("#") ? (
                <Link key={item.label} to={item.to} className="hover:text-ink">
                  {item.label}
                </Link>
              ) : (
                <NavLink
                  key={item.label}
                  to={item.to}
                  end
                  className={({ isActive }) => (isActive ? "text-ink" : "hover:text-ink")}
                >
                  {item.label}
                </NavLink>
              ),
            )}
          </nav>
          <div className="flex items-center gap-3">
            <Link to="/sources" className="text-[15px] font-medium text-muted hover:text-ink md:hidden">
              Sources
            </Link>
            <Link
              to="/profile"
              className="inline-flex min-h-11 items-center rounded-xl bg-brand px-4 font-bold text-white hover:bg-brand-dark"
            >
              Get started
            </Link>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <Outlet />
      </main>

      <footer className="border-t border-line bg-wash">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 px-4 py-8 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="font-extrabold">Rehnuma</p>
            <p className="text-sm text-muted">
              Planning help for university admissions in Pakistan. Not an admission guarantee.
            </p>
          </div>
          <nav aria-label="Footer" className="flex gap-5 text-[15px] font-semibold text-brand">
            <Link to="/profile" className="hover:underline">
              Build my plan
            </Link>
            <Link to="/sources" className="hover:underline">
              Sources
            </Link>
          </nav>
        </div>
      </footer>
    </div>
  );
}
