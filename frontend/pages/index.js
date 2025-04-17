import { useRouter } from "next/router";
import { motion } from "framer-motion";


export default function HomePage() {
  const router = useRouter();

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center justify-center min-h-screen relative"
    >
      {/* Gradient Background Animation */}
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

      {/* Content Box */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ duration: 1 }}
        className="relative z-10 text-center text-white"
      >
        <motion.h1
          initial={{ y: -200, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1 }}
          className="text-6xl font-bold"
        >
          Welcome to SummAIze
        </motion.h1>

        <motion.p
          initial={{ y: 200, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ duration: 1 }}
          className="text-xl mt-4"
        >
          Your AI-powered PDF summarizer
        </motion.p>

        {/* Animated Button */}
        <motion.button
          whileHover={{
            scale: 1.1,
            background: "linear-gradient(to right, #ff758c, #ff7eb3)",
          }}
          whileTap={{ scale: 0.9 }}
          animate={{ y: [0, -5, 0] }}
          transition={{ duration: 1.5, repeat: Infinity, repeatType: "reverse" }}
          className="mt-6 px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg shadow-lg transition-all"
          onClick={() => router.push("/login")}
        >
          Go to Login
        </motion.button>
        
      </motion.div>
     
    </motion.div>
  );
}
