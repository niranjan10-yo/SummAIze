import React, { useState } from "react";
import { useRouter } from "next/router";
import { motion } from "framer-motion";
import { loginUser } from "../services/api"; // ✅ Import API function
import Footer from "../components/Footer";

const Login = () => {
  const [formData, setFormData] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLogin = async () => {
    setLoading(true);
    setError("");

    try {
      const user = await loginUser(formData); // ✅ API call

      if (user && user.token && user.username) {  // ✅ Ensure username is received
        localStorage.setItem("token", user.token);
        localStorage.setItem("userId", user.id.toString());  // ✅ Fix: Store userId to string
        localStorage.setItem("username", user.username); // ✅ Store username
        router.push("/dashboard");
      } else {
        setError("Login failed: Invalid response from server.");
      }
    } catch (err) {
      setError(err.message || "Invalid credentials. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <motion.div className="flex h-screen" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
      {/* Background Animation */}
      <motion.div
        animate={{
          background: [
            "linear-gradient(to right, #6a11cb, #2575fc)",
            "linear-gradient(to right, #ff7eb3, #ff758c)",
            "linear-gradient(to right, #6a11cb, #2575fc)",
          ],
        }}
        transition={{ duration: 6, repeat: Infinity, repeatType: "mirror" }}
        className="absolute inset-0"
      />

      {/* Left Side: Branding */}
      <motion.div className="relative z-10 w-1/2 flex flex-col justify-center p-10 text-white"
        initial={{ x: -50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 1.2 }}>
        <h1 className="text-6xl font-bold">Welcome to SummAize</h1>
        <h2 className="text-3xl font-bold">AI-Powered Summarization</h2>
        <p className="mt-4 text-lg">Summarize PDFs quickly and efficiently with AI.</p>
      </motion.div>

      {/* Right Side: Login Form */}
      <motion.div className="relative z-10 w-1/2 flex justify-center items-center"
        initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 1.2 }}>
        <motion.div className="bg-white p-10 rounded-lg shadow-lg w-96" whileHover={{ scale: 1.05 }}>
          <h2 className="text-center text-lg font-semibold text-gray-700">USER LOGIN</h2>
          {error && <p className="text-red-500 text-center mt-2">{error}</p>}
          
          {/* Input Fields */}
          <div className="mt-5 space-y-3">
            <input type="email" name="email" placeholder="Email" className="w-full px-4 py-2 border rounded-lg"
              value={formData.email} onChange={handleChange} />
            <input type="password" name="password" placeholder="Password" className="w-full px-4 py-2 border rounded-lg"
              value={formData.password} onChange={handleChange} />

            {/* Login Button */}
            <motion.button className="w-full bg-purple-500 text-white py-2 rounded-lg mt-3" onClick={handleLogin} disabled={loading}
              whileTap={{ scale: 0.95 }} whileHover={{ background: "linear-gradient(to right, #ff758c, #ff7eb3, #ff758c)" }}>
              {loading ? "Logging in..." : "LOGIN"}
            </motion.button>

            {/* Signup Redirect */}
            <p className="text-center text-gray-600 mt-3">
              Don't have an account? 
              <span className="text-purple-500 cursor-pointer" onClick={() => router.push("/signup")}> Sign Up</span>
            </p>
          </div>
        </motion.div>
      </motion.div>

      {/* Footer */}
      <Footer />
    </motion.div>
  );
};

export default Login;
