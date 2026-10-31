
import CrudPage from "../../components/CrudPage";

export default function Plans() {
  return (
    <CrudPage
      title="Subscription Plans"
      endpoint="/plans/"
      fields={[
        {
          name: "product_id",
          label: "Product ID",
          type: "number",
          required: true,
          min: "1",
        },
        { name: "plan_name", label: "Plan Name", required: true },
        { name: "description", label: "Description" },
        { name: "billing_cycle", label: "Billing Cycle (Monthly/Yearly)", required: true },
        {
          name: "billing_interval",
          label: "Billing Interval",
          type: "number",
          required: true,
          min: "1",
        },
        {
          name: "price",
          label: "Price",
          type: "number",
          required: true,
          min: "0",
        },
        {
          name: "minimum_quantity",
          label: "Minimum Quantity",
          type: "number",
          min: "1",
        },
        {
          name: "maximum_quantity",
          label: "Maximum Quantity",
          type: "number",
          min: "1",
        },
        {
          name: "trial_days",
          label: "Trial Days",
          type: "number",
          min: "0",
        },
      ]}
      columns={[
        { key: "id", label: "ID" },
        { key: "plan_name", label: "Plan Name" },
        { key: "product_id", label: "Product ID" },
        { key: "billing_cycle", label: "Billing Cycle" },
        { key: "price", label: "Price" },
        { key: "status", label: "Status" },
      ]}
    />
  );
}
