import axios from "axios";
import API_BASE_URL from "../config";

const downloadFile = async (
  fileId: string,
  filename: string = "downloaded-file"
) => {
  try {
    const token = localStorage.getItem("token");
    if (!token) {
      throw new Error("Authentication token missing. Please login again.");
    }
    const response = await axios.get(
      `${API_BASE_URL}api/files/download/${fileId}/`,
      {
        responseType: "blob",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    const url = window.URL.createObjectURL(response.data);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error: unknown) {
    if (error instanceof Error) {
      alert(error.message);
      console.error(error);
    } else {
      alert("Error downloading file.");
      console.error(error);
    }
  }
};

export default downloadFile;
