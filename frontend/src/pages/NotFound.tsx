import { Link } from "react-router-dom";
import { EmptyState } from "../components/common";
export default function NotFound() {
  return (
    <EmptyState
      title="Page not found"
      description="This workspace page does not exist."
      action={<Link to="/timeline">Return to timeline</Link>}
    />
  );
}
