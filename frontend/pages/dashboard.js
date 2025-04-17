import React, { useState, useEffect } from "react";
import { uploadPDF, getSummary, saveSummary, submitFeedback,fetchSummaries } from "../services/api";
import { motion } from "framer-motion";
import { useRouter } from "next/router";
import { FaStar } from "react-icons/fa";

const Dashboard = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [feedback, setFeedback] = useState("");
  const [pdfId, setPdfId] = useState(null);
  const [loading, setLoading] = useState({ upload: false, summarize: false, feedback: false });
  const [username, setUsername] = useState("User");
  const [rating, setRating] = useState(5); 
  const [comment, setComment] = useState("");
  const [hover, setHover] = useState(null);
  const router = useRouter();
  const [summaries, setSummaries] = useState([]);
  const [summary, setSummary] = useState(""); // Store summary result
  //const [loading, setLoading] = useState(false);
  const [summarizeClicked, setSummarizeClicked] = useState(false); // Toggle state

  useEffect(() => {
    const token = localStorage.getItem("token");
    const storedUsername = localStorage.getItem("username") || "User";
  
    if (!token) {
      router.push("/login");
    } else {
      setUsername(storedUsername);
    }
  
    const getSummaries = async () => {
      try {
        const data = await fetchSummaries();
        console.log("Fetched Summaries:", data); // Debugging log
        setSummaries(data || []); // ✅ Ensure 'data' is at least an empty array
      } catch (error) {
        console.error("Error fetching summaries:", error);
        setSummaries([]); // ✅ Prevents errors if fetch fails
      }
    };
  
    getSummaries();
  }, [router, setSummaries]); // Added `setSummaries` as a dependency
  

  const handleLogout = () => {
    localStorage.removeItem("token");
    localStorage.removeItem("username");
    localStorage.removeItem("user_id")
    router.push("/login");
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };
  
  const handleUpload = async () => {
    if (!selectedFile) {
      alert("No file selected!");
      return;
    }
  
    console.log("📄 Selected File:", selectedFile.name); // Debugging log
  
    setLoading((prev) => ({ ...prev, upload: true }));
  
    try {
      const response = await uploadPDF(selectedFile); // ✅ Pass only `selectedFile`
      
      if (response?.pdf_id) {
        setPdfId(response.pdf_id);
        alert("✅ PDF uploaded successfully!");
        setSelectedFile(null); // Clear the file input
      } else {
        console.error("❌ Invalid response from backend:", response);
        alert("Upload failed. Please try again.");
      }
    } catch (error) {
      console.error("❌ Upload Error:", error);
      alert("Failed to upload PDF.");
    } finally {
      setLoading((prev) => ({ ...prev, upload: false }));
    }
  };
  // new added code for slecting model
  const [selectedModel, setSelectedModel] = useState("bart-large");
//------
/*const fetchSummaries = async () => {
  try {
    const response = await fetch("http://127.0.0.1:8000/summary/get_all_summaries/");
    if (!response.ok) throw new Error("Failed to fetch summaries");

    const data = await response.json();
    setSummaries(data || []); // Ensure it's an array
  } catch (error) {
    console.error("Error fetching summaries:", error);
    setSummaries([]); // Fallback to empty array
  }
};*/

//-----

// Call this function when the dashboard loads
useEffect(() => {
  console.log("Fetching summaries...");
  fetchSummaries()
    .then(() => console.log("Summaries fetched successfully"))
    .catch((error) => console.error("Error fetching summaries:", error));
}, []);

useEffect(() => {
  console.log("Updated Summary:", summary);
}, [summary]);


const handleSummarize = async () => {
  if (!pdfId) return alert("Upload a PDF first!");

  setLoading((prev) => ({ ...prev, summarize: true }));
  setSummarizeClicked(true);

  try {
    console.log("PDF ID:", pdfId, "Selected Model:", selectedModel);

    // Get summary directly - your getSummary function already returns the summary text
    const summaryText = await getSummary(pdfId, selectedModel);
    
    console.log("Received Summary:", summaryText);
    console.log("Type of Summary:", typeof summaryText);
    
    // If we got a valid summary
    if (summaryText) {
      setSummary(summaryText);
      console.log("Summary set in state successfully");
    } else {
      throw new Error("No summary received from API");
    }
  } catch (error) {
    console.error("Summary Fetch Error:", error.message || "Unknown error");
    alert("Failed to fetch summary. Please try again.");
  } finally {
    setLoading((prev) => ({ ...prev, summarize: false }));
  }
};



  const handleSaveSummary = async () => {
    if (!summary) {
        alert("No summary available.");
        return;
    }

    if (!pdfId) {
        alert("No associated PDF. Upload and summarize first!");
        return;
    }

    try {
        const response = await saveSummary({ pdf_id: pdfId, summary });

        if (response?.success) {  // Ensure response has a success field or relevant confirmation
            alert("✅ Summary saved successfully!");
        } else {
            throw new Error("Unexpected response format");
        }
    } catch (error) {
        console.error("Summary Save Error:", error);
        alert("❌ Failed to save summary. Please try again.");
    }
};

const handleSubmitFeedback = async () => {
  const userId = localStorage.getItem("userId"); // Fetch user ID
  if (!userId) {
    alert("User not found. Please log in again.");
    return;
  }
  
  if (!rating) {
    alert("Please select a rating!");
    return;
  }

  setLoading((prev) => ({ ...prev, feedback: true }));

  try {
    const response = await submitFeedback(userId, rating, comment);
    
    if (response) {
      alert("✅ Feedback submitted successfully!");
      setRating(5);  // Reset rating
      setComment("");  // Clear feedback
    } else {
      alert("❌ Failed to submit feedback.");
    }
  } catch (error) {
    console.error("Feedback Submission Error:", error);
    alert("❌ Error submitting feedback.");
  } finally {
    setLoading((prev) => ({ ...prev, feedback: false }));
  }
};

return (
  <motion.div className="flex flex-col items-center min-h-screen p-6 text-white relative overflow-hidden"
    initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}>
    
    {/* Background with gradient animation */}
    <motion.div className="absolute inset-0 z-[-1]" animate={{ background: [
      "linear-gradient(135deg, #6a11cb, #2575fc)",
      "linear-gradient(135deg, #8e2de2, #4a00e0)",
      "linear-gradient(135deg, #6a11cb, #2575fc)"
    ] }} transition={{ duration: 10, repeat: Infinity, ease: "linear" }} />

    {/* Header section */}
    <div className="w-full flex justify-between items-center p-4 mb-4">
      <h1 className="text-xl font-bold">Welcome, {username}!</h1>
      <h1 className="text-6xl font-bold text-white absolute left-1/2 transform -translate-x-1/2 drop-shadow-lg">SummAIze</h1>
      <motion.button whileHover={{ scale: 1.05 }} onClick={handleLogout} className="px-5 py-2 bg-[#FF007F] text-white font-semibold rounded-lg transition hover:bg-[#CC005F] shadow-lg">
        Logout
      </motion.button>
    </div>

    <p className="text-center text-lg text-white my-6 max-w-xl bg-black/20 p-4 rounded-lg backdrop-blur-sm">
      "SummAIze helps you save time by generating concise summaries of research papers and study materials. Upload, summarize, and stay efficient!"
    </p>

    {/* Upload and Model Selection */}
    <div className="grid grid-cols-2 gap-8 w-full max-w-4xl mb-8">
      <div className="bg-white/10 p-6 rounded-xl backdrop-blur-sm shadow-lg">
        <h2 className="text-xl font-semibold text-white mb-3">Upload PDF</h2>
        <input type="file" accept="application/pdf" onChange={handleFileChange} className="mt-3 w-full p-2 text-black rounded border border-gray-400 bg-white/90" />
        <motion.button whileHover={{ scale: 1.05 }} onClick={handleUpload} disabled={loading.upload} className="mt-4 px-5 py-3 w-full bg-[#00FFD1] text-black font-semibold rounded-lg transition hover:bg-[#00CCA0] disabled:opacity-50 shadow-md">
          {loading.upload ? "Uploading..." : "Upload PDF"}
        </motion.button>
      </div>
      
      <div className="bg-white/10 p-6 rounded-xl backdrop-blur-sm shadow-lg">
        <h2 className="text-xl font-semibold text-white mb-3">Select Model</h2>
        <select
          className="mt-3 w-full p-2 border rounded text-black bg-white/90"
          value={selectedModel}
          onChange={(e) => setSelectedModel(e.target.value)}
        >
          <option value="pretrained">BART-Large</option>
          <option value="fine-tuned">Fine-Tuned BART</option>
        </select>
        <motion.button 
          whileHover={{ scale: 1.05 }} 
          onClick={handleSummarize} 
          disabled={loading.summarize} 
          className="mt-4 px-5 py-3 w-full bg-[#2575fc] text-white font-semibold rounded-lg transition hover:bg-[#1a56d8] disabled:opacity-50 shadow-md">
          {loading.summarize ? "Summarizing..." : "Summarize"}
        </motion.button>
      </div>
    </div>

    {/* Summary and Feedback side by side */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-8 w-full max-w-6xl">
      {/* Summary section */}
      <div className="bg-white p-6 rounded-xl shadow-xl transform transition-all duration-300 hover:shadow-2xl">
        <h2 className="text-xl font-semibold text-[#00FFD1] mb-4">Summary</h2>
        <div className="bg-gray-50 p-4 rounded-lg min-h-[200px] border border-gray-100">
          <p className="text-gray-800 whitespace-pre-line">
            {summary ? summary : "Your summary will appear here..."}
            </p>
        </div>
      </div>

      {/* Feedback section */}
      <div className="bg-white p-6 rounded-xl shadow-xl transform transition-all duration-300 hover:shadow-2xl">
        <h2 className="text-xl font-semibold text-[#0000FF] mb-4">Feedback</h2>
        <textarea 
          className="w-full p-4 mt-2 border rounded-lg bg-gray-50 min-h-[100px] text-black placeholder-gray-500" 
          value={comment} 
          onChange={(e) => setComment(e.target.value)} 
          placeholder="Enter your feedback here..." 
        />
        
        <div className="flex items-center space-x-2 mt-4 mb-4">
          <span className="font-medium">Rating:</span>
          {[1, 2, 3, 4, 5].map((star) => (
            <FaStar
              key={star}
              size={30}
              className="cursor-pointer transition-colors duration-200"
              color={star <= (hover || rating) ? "#ffc107" : "#e4e5e9"}
              onMouseEnter={() => setHover(star)}
              onMouseLeave={() => setHover(null)}
              onClick={() => setRating(star)}
            />
          ))}
        </div>
        
        <motion.button 
          whileHover={{ scale: 1.02 }} 
          whileTap={{ scale: 0.98 }}
          onClick={handleSubmitFeedback} 
          className="mt-2 px-5 py-3 w-full bg-gradient-to-r from-[#00FFD1] to-[#00CCA0] text-black font-semibold rounded-lg transition hover:from-[#00CCA0] hover:to-[#00A880] shadow-md"
        >
          Submit Feedback
        </motion.button>
      </div>
    </div>
  </motion.div>
);
};

export default Dashboard;
