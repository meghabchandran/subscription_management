
import CrudPage from "../../components/CrudPage";

export default function Variants() {
  return (
    <CrudPage
      title="Product Variants"
      endpoint="/variants/"
      fields={[
        {
          name: "product_id",
          label: "Product ID",
          type: "number",
          required: true,
          min: "1",
        },
        { name: "variant_name", label: "Variant Name", required: true },
        { name: "variant_code", label: "Variant Code", required: true },
        { name: "description", label: "Description" },
        {
          name: "additional_price",
          label: "Additional Price",
          type: "number",
          min: "0",
        },
      ]}
      columns={[
        { key: "id", label: "ID" },
        { key: "product_id", label: "Product ID" },
        { key: "variant_name", label: "Variant Name" },
        { key: "variant_code", label: "Variant Code" },
        { key: "additional_price", label: "Extra Price" },
        { key: "status", label: "Status" },
      ]}
    />
  );
}
