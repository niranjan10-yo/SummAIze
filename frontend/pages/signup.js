import React, { useState } from "react";
import { useRouter } from "next/router";
import { motion } from "framer-motion";
import { registerUser } from "../services/api"; // ✅ Import API function
import Footer from "../components/Footer";

const Signup = () => {
  const [formData, setFormData] = useState({
    username: "", 
    email: "", 
    password: "", 
    confirmPassword: ""
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const router = useRouter();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSignup = async () => {
    setError("");
    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setLoading(true);
    try {
      await registerUser({
        username: formData.username,  // ✅ Correct field
        email: formData.email,
        password: formData.password,
      });

      router.push("/dashboard");
    } catch (error) {
      setError(error.response?.data?.detail || "Signup failed. Try again.");
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
            "linear-gradient(to right, #6a11cb, #2575fc)"
          ],
        }}
        transition={{ duration: 6, repeat: Infinity, repeatType: "mirror" }}
        className="absolute inset-0"
      />

      {/* Left Side: Branding */}
      <motion.div className="relative z-10 w-1/2 flex flex-col justify-center p-10 text-white"
        initial={{ x: -50, opacity: 0 }} animate={{ x: 0, opacity: 1 }} transition={{ duration: 1.2 }}>
        <h1 className="text-6xl font-bold">Join SummAIze</h1>
        <h2 className="text-3xl font-bold">Sign up and start summarizing</h2>
        <p className="mt-4 text-lg">Create an account and enjoy AI-powered summarization.</p>
      </motion.div>

      {/* Right Side: Signup Form */}
      <motion.div className="relative z-10 w-1/2 flex justify-center items-center"
        initial={{ scale: 0.7, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 1.2 }}>
        <motion.div className="bg-white p-10 rounded-lg shadow-lg w-96" whileHover={{ scale: 1.05 }}>
          <h2 className="text-center text-lg font-semibold text-gray-700">USER SIGN UP</h2>
          {error && <p className="text-red-500 text-center mt-2">{error}</p>}
          
          {/* Input Fields */}
          <div className="mt-5 space-y-3">
            <input type="text" name="username" placeholder="Full Name" className="w-full px-4 py-2 border rounded-lg"
              value={formData.username} onChange={handleChange} />
            <input type="email" name="email" placeholder="Email" className="w-full px-4 py-2 border rounded-lg"
              value={formData.email} onChange={handleChange} />
            <input type="password" name="password" placeholder="Password" className="w-full px-4 py-2 border rounded-lg"
              value={formData.password} onChange={handleChange} />
            <input type="password" name="confirmPassword" placeholder="Confirm Password" className="w-full px-4 py-2 border rounded-lg"
              value={formData.confirmPassword} onChange={handleChange} />

            {/* Signup Button */}
            <motion.button className="w-full bg-purple-500 text-white py-2 rounded-lg" onClick={handleSignup} disabled={loading}
              whileTap={{ scale: 0.95 }} whileHover={{ background: "linear-gradient(to right, #ff758c, #ff7eb3, #ff758c)" }}>
              {loading ? "Signing up..." : "SIGN UP"}
            </motion.button>

            {/* Login Redirect */}
            <p className="text-center text-gray-600">
              Already have an account? 
              <span className="text-purple-500 cursor-pointer" onClick={() => router.push("/login")}> Login</span>
            </p>
          </div>
        </motion.div>
      </motion.div>
      
      {/* Footer */}
      <Footer />
    </motion.div>
  );
};

export default Signup;
