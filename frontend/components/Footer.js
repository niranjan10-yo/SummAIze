import { motion } from "framer-motion";
const Footer = () => {
    return (
        <motion.footer
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 1, ease: "easeInOut" }}
       className="text-1xl font-bold fixed bottom-0 left-0 w-full text-center py-4 text-white  text-sm">
        © 2025  <span className="font-semibold">SummAIze</span>. All rights reserved.
      </motion.footer>
    );
  };
  
  export default Footer;
  