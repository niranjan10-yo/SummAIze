import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000"; // Adjust if necessary

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

// Helper function for handling API requests
const handleRequest = async (requestFunc, logLabel = "API Request") => {
  try {
    const response = await requestFunc();
    console.log(`${logLabel} Success:`, response.data); // Log successful responses
    return response.data;
  } catch (error) {
    console.error(`${logLabel} Error:`, error.response?.data || error.message);
    throw error;
  }
};

// 🔹 User Authentication
export const loginUser = (userData) => handleRequest(() => api.post("/auth/login", userData), "Login");
export const registerUser = (userData) => handleRequest(() => api.post("/auth/register", userData), "Register");

// 🔹 Upload PDF
export const uploadPDF = async (file) => {
  const formData = new FormData();
  formData.append("file", file);  // No need to include file.name

  console.log("📤 Sending PDF:", file.name); // Debugging

  try {
    const response = await axios.post("http://127.0.0.1:8000/pdf/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    console.log("✅ Upload Success:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Upload Error:", error.response?.data || error.message);
    alert(`Upload failed: ${error.response?.data?.detail || "Try again."}`);
    return null;
  }
};


// 🔹 Get Summary
export const getSummary = async (pdfId, model) => {
  const userId = localStorage.getItem("userId") || 1;
  console.log("Retrieved userId from localStorage:", userId);
  
  if (!pdfId) {
    alert("❌ Missing PDF ID!");
    return null;
  }
  
  if (!userId || isNaN(userId)) {
    alert("❌ Missing or Invalid User ID!");
    return null;
  }
  
  // Map frontend model names to backend model types if needed
  let modelType = model;
  if (model === "bart-large") {
    modelType = "pretrained";
  }
  
  const numericUserId = parseInt(userId, 10);
  const requestData = {
    pdf_id: pdfId,
    user_id: numericUserId,
    model_type: modelType,  // ✅ FIXED: Changed from "model" to "model_type"
  };
  
  console.log(`[getSummary] 📤 Request Sent: ${JSON.stringify(requestData)}`);
  
  try {
    const response = await axios.post("http://127.0.0.1:8000/summary/summarize/", requestData, {
      headers: { "Content-Type": "application/json" },
    });
    
    if (!response.data || !response.data.summary) {
      throw new Error("Invalid API response: No summary found.");
    }
    
    const summaryText = response.data.summary;
    console.log("✅ Extracted Summary:", summaryText);
    console.log("✅ Model Used:", response.data.model_used);
    return summaryText;
  } catch (error) {
    console.error("❌ API Error:", error.response?.data || error.message);
    const errorMessage =
      error.response?.data?.detail || "Summarization failed. Please try again.";
    alert(`❌ ${errorMessage}`);
    return null;
  }
};



// 🔹 Save Summary
export const saveSummary = (summaryData) => handleRequest(() => api.post("/save-summary", summaryData), "Save Summary");

// 🔹 Submit Feedback
export const submitFeedback = async (userId, rating, comment) => {
  if (!comment.trim()) {
    alert("Feedback comment cannot be empty!");
    return;
  }

  console.log("📤 Sending Feedback:", { userId, rating, comment });  // Debugging log

  try {
    const response = await axios.post("http://127.0.0.1:8000/feedback/submit", {
      user_id: userId,
      rating: rating,
      comment: comment.trim()  // ✅ Ensure empty spaces are removed
    });

    console.log("✅ Feedback Submitted:", response.data);
    return response.data;
  } catch (error) {
    console.error("❌ Feedback Submission Error:", error.response?.data || error.message);
    alert(`Failed to submit feedback: ${error.response?.data?.detail || "Try again."}`);
    return null;
  }
};

export const fetchSummaries = async () => {
  try {
      const response = await fetch("http://127.0.0.1:8000/summary/get_all_summaries/");
      if (!response.ok) {
          throw new Error("Failed to fetch summaries");
      }
      return await response.json();
  } catch (error) {
      console.error("Error fetching summaries:", error);
      return [];
  }
};




export default api;
