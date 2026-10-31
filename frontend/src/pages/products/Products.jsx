
import CrudPage from "../../components/CrudPage";

export default function Products() {
  return (
    <CrudPage
      title="Products"
      endpoint="/products/"
      fields={[
        { name: "product_name", label: "Product Name", required: true },
        { name: "product_code", label: "Product Code", required: true },
        { name: "description", label: "Description" },
        { name: "category", label: "Category" },
        {
          name: "base_price",
          label: "Base Price",
          type: "number",
          required: true,
          min: "0",
        },
      ]}
      columns={[
        { key: "id", label: "ID" },
        { key: "product_name", label: "Product Name" },
        { key: "product_code", label: "Product Code" },
        { key: "category", label: "Category" },
        { key: "base_price", label: "Price" },
        { key: "status", label: "Status" },
      ]}
    />
  );
}
