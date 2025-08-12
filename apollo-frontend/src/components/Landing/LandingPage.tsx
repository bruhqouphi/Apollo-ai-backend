import React, { useState, useEffect, useRef } from 'react';
import { motion, useScroll, useTransform, useSpring } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { 
  Brain, 
  BarChart3, 
  Activity,
  ArrowRight,
  CheckCircle,
  Rocket,
  Eye,
  Cpu,
  Play,
  X
} from 'lucide-react';

// Import Apollo images
import apollo1 from '../../assets/Apollo 1.jpg';
import apollo2 from '../../assets/Apollo 2.jpg';
import apollo3 from '../../assets/Apollo 3.jpg';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [selectedImage, setSelectedImage] = useState<number | null>(null);
  const [isImageExpanded, setIsImageExpanded] = useState(false);
  
  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start start", "end start"]
  });

  const y = useTransform(scrollYProgress, [0, 1], ["0%", "50%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.5], [1, 0]);
  const scale = useTransform(scrollYProgress, [0, 1], [1, 0.8]);

  const springY = useSpring(y, { stiffness: 100, damping: 30 });
  const springOpacity = useSpring(opacity, { stiffness: 100, damping: 30 });

  // Mouse tracking for 3D effects
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Enhanced 3D Parallax Effect
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const cards = document.querySelectorAll('.parallax-card');
      const images = document.querySelectorAll('.parallax-image');
      
      cards.forEach((card) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const rotateX = (y - centerY) / 15;
        const rotateY = (centerX - x) / 15;
        
        (card as HTMLElement).style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
      });

      images.forEach((image) => {
        const rect = image.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;
        
        const centerX = rect.width / 2;
        const centerY = rect.height / 2;
        
        const moveX = (x - centerX) / 20;
        const moveY = (y - centerY) / 20;
        
        (image as HTMLElement).style.transform = `translate3d(${moveX}px, ${moveY}px, 0px) scale(1.1)`;
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Handle image click for zoom effect
  const handleImageClick = (index: number) => {
    setSelectedImage(index);
    setIsImageExpanded(true);
    document.body.style.overflow = 'hidden';
  };

  // Handle close zoom effect
  const handleCloseZoom = () => {
    setIsImageExpanded(false);
    setSelectedImage(null);
    document.body.style.overflow = 'auto';
  };

  // Handle escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isImageExpanded) {
        handleCloseZoom();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [isImageExpanded]);

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Insights",
      description: "Get intelligent data analysis and actionable insights powered by advanced AI algorithms",
      color: "from-purple-500 to-pink-500",
      glow: "shadow-purple-500/50"
    },
    {
      icon: BarChart3,
      title: "Interactive Visualizations",
      description: "Create stunning charts and graphs with our advanced visualization engine",
      color: "from-blue-500 to-cyan-500",
      glow: "shadow-blue-500/50"
    },
    {
      icon: Activity,
      title: "Seamless Upload",
      description: "Drag and drop your data files with instant processing and validation",
      color: "from-green-500 to-emerald-500",
      glow: "shadow-green-500/50"
    },
    {
      icon: CheckCircle,
      title: "Enterprise Security",
      description: "Bank-level security with end-to-end encryption and compliance standards",
      color: "from-orange-500 to-red-500",
      glow: "shadow-orange-500/50"
    }
  ];

  const testimonials = [
    {
      name: "Sarah Johnson",
      role: "Data Scientist",
      company: "TechCorp",
      content: "Apollo AI transformed our data analysis workflow. The insights are incredible!",
      rating: 5,
      avatar: "👩‍💻"
    },
    {
      name: "Michael Chen",
      role: "Analytics Director",
      company: "DataFlow Inc",
      content: "The visualization capabilities are unmatched. Our presentations have never looked better.",
      rating: 5,
      avatar: "👨‍💼"
    },
    {
      name: "Emily Rodriguez",
      role: "Business Analyst",
      company: "GrowthMetrics",
      content: "Intuitive interface with powerful features. Perfect for both beginners and experts.",
      rating: 5,
      avatar: "👩‍🔬"
    }
  ];

  const stats = [
    { number: "10K+", label: "Active Users", icon: Eye },
    { number: "50M+", label: "Data Points Analyzed", icon: Cpu },
    { number: "99.9%", label: "Uptime", icon: CheckCircle },
    { number: "24/7", label: "Support", icon: Rocket }
  ];

  const apolloImages = [
    { 
      src: apollo1, 
      title: "Advanced AI Engine", 
      description: "State-of-the-art machine learning algorithms",
      details: "Our AI engine processes millions of data points in real-time, providing instant insights and predictions. Built with cutting-edge neural networks and deep learning models.",
      features: ["Real-time processing", "Predictive analytics", "Pattern recognition", "Natural language understanding"]
    },
    { 
      src: apollo2, 
      title: "Data Processing", 
      description: "High-performance data analysis capabilities",
      details: "Transform raw data into actionable insights with our powerful processing engine. Handle any data format, size, or complexity with enterprise-grade performance.",
      features: ["Multi-format support", "Scalable architecture", "Data validation", "Quality assurance"]
    },
    { 
      src: apollo3, 
      title: "Visual Intelligence", 
      description: "Next-generation visualization technology",
      details: "Create stunning, interactive visualizations that tell your data's story. Our visual intelligence system automatically selects the best chart types and layouts.",
      features: ["Auto-chart selection", "Interactive dashboards", "Real-time updates", "Export capabilities"]
    }
  ];

  return (
    <div ref={containerRef} className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 overflow-hidden">
      {/* Enhanced Animated Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        {/* Floating Orbs with Glow */}
        <motion.div 
          animate={{ 
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1]
          }}
          transition={{ 
            duration: 20, 
            repeat: Infinity, 
            ease: "easeInOut" 
          }}
          className="absolute -top-40 -right-40 w-80 h-80 bg-blue-500/20 rounded-full blur-3xl animate-float shadow-2xl shadow-blue-500/30"
        />
        <motion.div 
          animate={{ 
            x: [0, -100, 0],
            y: [0, 50, 0],
            scale: [1, 0.8, 1]
          }}
          transition={{ 
            duration: 25, 
            repeat: Infinity, 
            ease: "easeInOut",
            delay: 2
          }}
          className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-float shadow-2xl shadow-purple-500/30"
        />
        <motion.div 
          animate={{ 
            x: [0, 80, 0],
            y: [0, -80, 0],
            scale: [1, 1.1, 1]
          }}
          transition={{ 
            duration: 30, 
            repeat: Infinity, 
            ease: "easeInOut",
            delay: 4
          }}
          className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl animate-float shadow-2xl shadow-cyan-500/20"
        />
        
        {/* Enhanced Grid Pattern */}
        <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]" />
        
        {/* Particle Effect */}
        <div className="absolute inset-0">
          {[...Array(50)].map((_, i) => (
            <motion.div
              key={i}
              className="absolute w-1 h-1 bg-white/20 rounded-full"
              style={{
                left: `${Math.random() * 100}%`,
                top: `${Math.random() * 100}%`,
              }}
              animate={{
                y: [0, -100, 0],
                opacity: [0, 1, 0],
              }}
              transition={{
                duration: Math.random() * 3 + 2,
                repeat: Infinity,
                delay: Math.random() * 2,
              }}
            />
          ))}
        </div>
      </div>

      {/* Navigation Header */}
      <motion.header
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="fixed top-0 left-0 right-0 z-50 p-6"
      >
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <motion.div 
            className="flex items-center space-x-3"
            whileHover={{ scale: 1.05 }}
          >
            <motion.div 
              className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-500/50"
              animate={{ 
                boxShadow: [
                  "0 0 20px rgba(59, 130, 246, 0.5)",
                  "0 0 40px rgba(147, 51, 234, 0.5)",
                  "0 0 20px rgba(59, 130, 246, 0.5)"
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              {/* Zap icon removed */}
            </motion.div>
            <span className="text-xl font-bold text-gradient">Apollo AI</span>
          </motion.div>
          
          <div className="hidden md:flex items-center space-x-8">
            <motion.a 
              href="#features" 
              className="text-white/70 hover:text-white transition-colors relative group"
              whileHover={{ scale: 1.05 }}
            >
              Features
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </motion.a>
            <motion.a 
              href="#testimonials" 
              className="text-white/70 hover:text-white transition-colors relative group"
              whileHover={{ scale: 1.05 }}
            >
              Testimonials
              <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 group-hover:w-full transition-all duration-300"></span>
            </motion.a>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-white/10 backdrop-blur-xl border border-white/20 text-white font-semibold rounded-xl hover:bg-white/20 transition-all duration-300 shadow-lg hover:shadow-white/20"
            >
              Go to Dashboard
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <motion.section 
        style={{ y: springY, opacity: springOpacity, scale }}
        className="relative z-10 min-h-screen flex items-center justify-center px-4"
      >
        <div className="max-w-7xl mx-auto text-center">
          {/* Enhanced Badge */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center space-x-2 bg-white/10 backdrop-blur-xl border border-white/20 rounded-full px-6 py-3 mb-8 shadow-lg hover:shadow-white/20 transition-all duration-300"
            whileHover={{ scale: 1.05 }}
          >
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
            >
              {/* Sparkles icon removed */}
            </motion.div>
            <span className="text-white/80 text-sm font-medium">AI-Powered Data Intelligence Platform</span>
          </motion.div>

          {/* Main Heading with Glow Effect */}
          <motion.h1
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-5xl md:text-7xl font-bold mb-6"
          >
            <motion.span 
              className="text-gradient"
              animate={{ 
                textShadow: [
                  "0 0 20px rgba(59, 130, 246, 0.5)",
                  "0 0 40px rgba(147, 51, 234, 0.5)",
                  "0 0 20px rgba(59, 130, 246, 0.5)"
                ]
              }}
              transition={{ duration: 2, repeat: Infinity }}
            >
              Transform
            </motion.span>
            <br />
            <span className="text-white">Your Data</span>
            <br />
            <motion.span 
              className="text-gradient"
              animate={{ 
                textShadow: [
                  "0 0 20px rgba(147, 51, 234, 0.5)",
                  "0 0 40px rgba(59, 130, 246, 0.5)",
                  "0 0 20px rgba(147, 51, 234, 0.5)"
                ]
              }}
              transition={{ duration: 2, repeat: Infinity, delay: 1 }}
            >
              With AI
            </motion.span>
          </motion.h1>

          {/* Subtitle */}
          <motion.p
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-xl md:text-2xl text-white/70 mb-8 max-w-3xl mx-auto leading-relaxed"
          >
            Upload your data and get instant AI-powered insights, beautiful visualizations, and actionable recommendations in seconds.
          </motion.p>

          {/* Enhanced CTA Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.8 }}
            className="flex flex-col sm:flex-row items-center justify-center space-y-4 sm:space-y-0 sm:space-x-6 mb-12"
          >
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/dashboard')}
              className="group relative px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-2xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 overflow-hidden"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-700"
                initial={{ x: "-100%" }}
                whileHover={{ x: "0%" }}
                transition={{ duration: 0.3 }}
              />
              <span className="relative z-10 flex items-center space-x-2">
                <span>Get Started Free</span>
                <motion.div
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-5 h-5" />
                </motion.div>
              </span>
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="group flex items-center space-x-2 px-8 py-4 bg-white/10 backdrop-blur-xl border border-white/20 text-white font-semibold rounded-2xl hover:bg-white/20 transition-all duration-300 shadow-lg hover:shadow-white/20"
            >
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <Play className="w-5 h-5" />
              </motion.div>
              <span>Watch Demo</span>
            </motion.button>
          </motion.div>

          {/* Enhanced Stats with Icons */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1 }}
            className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto"
          >
            {stats.map((stat, index) => {
              const IconComponent = stat.icon;
              return (
                <motion.div 
                  key={stat.label} 
                  className="text-center group"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 1.2 + index * 0.1 }}
                  whileHover={{ scale: 1.05 }}
                >
                  <motion.div 
                    className="w-16 h-16 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-2xl flex items-center justify-center mx-auto mb-4 backdrop-blur-xl border border-white/10"
                    whileHover={{ 
                      boxShadow: "0 0 30px rgba(59, 130, 246, 0.3)",
                      scale: 1.1
                    }}
                  >
                    <IconComponent className="w-8 h-8 text-blue-400" />
                  </motion.div>
                  <motion.div 
                    className="text-3xl md:text-4xl font-bold text-gradient mb-2"
                    whileHover={{ scale: 1.1 }}
                  >
                    {stat.number}
                  </motion.div>
                  <div className="text-white/60 text-sm">{stat.label}</div>
                </motion.div>
              );
            })}
          </motion.div>
        </div>
      </motion.section>

      {/* Apollo Images Showcase with Scroll-Triggered Zoom */}
      <section className="relative z-10 py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Powered by <span className="text-gradient">Apollo Technology</span>
            </h2>
            <p className="text-xl text-white/70 max-w-3xl mx-auto">
              Experience the cutting-edge technology that drives our AI platform. Scroll to explore our advanced AI engine in detail.
            </p>
          </motion.div>

          {/* Single Image with Scroll Zoom Effect */}
          <ScrollZoomImage
            image={apolloImages[0]}
            index={0}
            totalImages={1}
          />

          {/* Other two images in normal grid layout */}
          <div className="grid md:grid-cols-2 gap-8 mt-20">
            {apolloImages.slice(1).map((image, index) => (
              <motion.div
                key={index + 1}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.2 }}
                viewport={{ once: true }}
                className="group cursor-pointer"
                whileHover={{ scale: 1.05 }}
                onClick={() => handleImageClick(index + 1)}
              >
                <div className="relative overflow-hidden rounded-2xl glass-card p-6">
                  <motion.img
                    src={image.src}
                    alt={image.title}
                    className="w-full h-64 object-cover rounded-xl parallax-image mb-6 transition-transform duration-300 group-hover:scale-110"
                  />
                  <h3 className="text-xl font-semibold text-white mb-2">{image.title}</h3>
                  <p className="text-white/60 mb-4">{image.description}</p>
                  
                  {/* Click indicator */}
                  <motion.div
                    className="flex items-center space-x-2 text-blue-400 text-sm"
                    initial={{ opacity: 0 }}
                    whileHover={{ opacity: 1 }}
                  >
                    <Play className="w-4 h-4" />
                    <span>Click to explore</span>
                  </motion.div>
                  
                  {/* Glow Effect */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    style={{
                      background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.1) 0%, transparent 50%)`
                    }}
                  />
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced Features Section */}
      <section id="features" className="relative z-10 py-20 px-4 bg-white/5">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Why Choose <span className="text-gradient">Apollo AI</span>?
            </h2>
            <p className="text-xl text-white/70 max-w-3xl mx-auto">
              Experience the future of data analysis with our cutting-edge AI platform
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="parallax-card glass-card p-8 text-center hover:scale-105 transition-all duration-300 group"
                  whileHover={{ 
                    boxShadow: `0 0 40px ${feature.glow}`,
                    scale: 1.05
                  }}
                >
                  <motion.div 
                    className={`w-16 h-16 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg`}
                    whileHover={{ 
                      scale: 1.2,
                      rotate: 360
                    }}
                    transition={{ duration: 0.5 }}
                  >
                    <IconComponent className="w-8 h-8 text-white" />
                  </motion.div>
                  <h3 className="text-xl font-semibold text-white mb-4">{feature.title}</h3>
                  <p className="text-white/60 leading-relaxed">{feature.description}</p>
                  
                  {/* Hover Glow Effect */}
                  <motion.div
                    className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300"
                    style={{
                      background: `radial-gradient(circle at ${mousePosition.x}px ${mousePosition.y}px, rgba(59, 130, 246, 0.1) 0%, transparent 50%)`
                    }}
                  />
                </motion.div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Enhanced Testimonials Section */}
      <section id="testimonials" className="relative z-10 py-20 px-4">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6">
              Trusted by <span className="text-gradient">Thousands</span>
            </h2>
            <p className="text-xl text-white/70">
              See what our users have to say about Apollo AI
            </p>
          </motion.div>

          <div className="grid md:grid-cols-3 gap-8">
            {testimonials.map((testimonial, index) => (
              <motion.div
                key={testimonial.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass-card p-8 group hover:scale-105 transition-all duration-300"
                whileHover={{ 
                  boxShadow: "0 0 40px rgba(59, 130, 246, 0.2)"
                }}
              >
                <div className="flex items-center space-x-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <motion.div
                      key={i}
                      initial={{ scale: 0 }}
                      animate={{ scale: 1 }}
                      transition={{ delay: index * 0.1 + i * 0.1 }}
                    >
                      {/* Star icon removed */}
                    </motion.div>
                  ))}
                </div>
                <p className="text-white/80 mb-6 leading-relaxed">"{testimonial.content}"</p>
                <div className="flex items-center space-x-3">
                  <motion.div 
                    className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-2xl"
                    whileHover={{ scale: 1.2, rotate: 360 }}
                    transition={{ duration: 0.5 }}
                  >
                    {testimonial.avatar}
                  </motion.div>
                  <div>
                    <div className="font-semibold text-white">{testimonial.name}</div>
                    <div className="text-white/60 text-sm">{testimonial.role} at {testimonial.company}</div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Enhanced CTA Section */}
      <section className="relative z-10 py-20 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="glass-card p-12 relative overflow-hidden"
            whileHover={{ scale: 1.02 }}
          >
            {/* Background Glow */}
            <motion.div
              className="absolute inset-0 opacity-50"
              animate={{
                background: [
                  "radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)",
                  "radial-gradient(circle at 80% 50%, rgba(147, 51, 234, 0.1) 0%, transparent 50%)",
                  "radial-gradient(circle at 20% 50%, rgba(59, 130, 246, 0.1) 0%, transparent 50%)"
                ]
              }}
              transition={{ duration: 4, repeat: Infinity }}
            />
            
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 relative z-10">
              Ready to <span className="text-gradient">Transform</span> Your Data?
            </h2>
            <p className="text-xl text-white/70 mb-8 relative z-10">
              Join thousands of users who are already leveraging the power of AI for their data analysis
            </p>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => navigate('/dashboard')}
              className="group relative px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-2xl shadow-2xl hover:shadow-blue-500/25 transition-all duration-300 overflow-hidden z-10"
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-700"
                initial={{ x: "-100%" }}
                whileHover={{ x: "0%" }}
                transition={{ duration: 0.3 }}
              />
              <span className="relative z-10 flex items-center space-x-2">
                <span>Start Your Free Trial</span>
                <motion.div
                  animate={{ x: [0, 5, 0] }}
                  transition={{ duration: 1.5, repeat: Infinity }}
                >
                  <ArrowRight className="w-5 h-5" />
                </motion.div>
              </span>
            </motion.button>
          </motion.div>
        </div>
      </section>

      {/* Image Zoom Modal */}
      {isImageExpanded && selectedImage !== null && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-black/90 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={handleCloseZoom}
        >
          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.8, opacity: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="relative max-w-6xl w-full max-h-[90vh] overflow-hidden rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Close button */}
            <button
              onClick={handleCloseZoom}
              className="absolute top-4 right-4 z-10 w-10 h-10 bg-black/50 rounded-full flex items-center justify-center text-white hover:bg-black/70 transition-colors"
            >
              <X className="w-5 h-5" />
            </button>

            <div className="flex flex-col lg:flex-row h-full">
              {/* Image section */}
              <div className="lg:w-1/2 p-6">
                <motion.img
                  src={apolloImages[selectedImage].src}
                  alt={apolloImages[selectedImage].title}
                  className="w-full h-64 lg:h-full object-cover rounded-xl"
                  initial={{ scale: 1 }}
                  whileHover={{ scale: 1.05 }}
                  transition={{ duration: 0.3 }}
                />
              </div>

              {/* Content section */}
              <div className="lg:w-1/2 p-6 flex flex-col justify-center">
                <motion.h3
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                  className="text-3xl font-bold text-white mb-4"
                >
                  {apolloImages[selectedImage].title}
                </motion.h3>
                
                <motion.p
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                  className="text-white/80 mb-6 leading-relaxed"
                >
                  {apolloImages[selectedImage].details}
                </motion.p>

                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.4 }}
                  className="space-y-3"
                >
                  <h4 className="text-lg font-semibold text-white mb-3">Key Features:</h4>
                  {apolloImages[selectedImage].features.map((feature, index) => (
                    <motion.div
                      key={feature}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.5 + index * 0.1 }}
                      className="flex items-center space-x-3"
                    >
                      <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                      <span className="text-white/70">{feature}</span>
                    </motion.div>
                  ))}
                </motion.div>

                <motion.button
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.6 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  onClick={() => navigate('/dashboard')}
                  className="mt-8 px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300"
                >
                  Try This Feature
                </motion.button>
              </div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </div>
  );
};

// Scroll Zoom Image Component
interface ScrollZoomImageProps {
  image: {
    src: string;
    title: string;
    description: string;
    details: string;
    features: string[];
  };
  index: number;
  totalImages: number;
}

const ScrollZoomImage: React.FC<ScrollZoomImageProps> = ({ image, index, totalImages }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const imageRef = useRef<HTMLImageElement>(null);
  const navigate = useNavigate();

  const { scrollYProgress } = useScroll({
    target: containerRef,
    offset: ["start end", "end start"]
  });

  // Transform values for the zoom effect
  const scale = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [1, 1.2, 3, 3]);
  const opacity = useTransform(scrollYProgress, [0, 0.2, 0.8, 1], [1, 1, 0.8, 0]);
  const y = useTransform(scrollYProgress, [0, 0.5, 1], [0, -50, -100]);
  const textOpacity = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [1, 1, 0, 0]);
  const textY = useTransform(scrollYProgress, [0, 0.3, 0.7, 1], [0, 0, -100, -200]);

  // Content that appears when image is zoomed
  const contentOpacity = useTransform(scrollYProgress, [0.4, 0.6, 0.8, 1], [0, 1, 1, 0]);
  const contentY = useTransform(scrollYProgress, [0.4, 0.6, 0.8, 1], [100, 0, 0, -100]);

  return (
    <div 
      ref={containerRef} 
      className="relative min-h-screen flex items-center justify-center mb-20"
      style={{ zIndex: totalImages - index }}
    >
      {/* Background overlay that appears during zoom */}
      <motion.div
        className="absolute inset-0 bg-black/50"
        style={{ opacity: useTransform(scrollYProgress, [0.3, 0.7], [0, 0.8]) }}
      />

      {/* Main image with zoom effect */}
      <motion.div
        className="relative w-full max-w-4xl mx-auto"
        style={{ scale, opacity, y }}
      >
        <motion.img
          ref={imageRef}
          src={image.src}
          alt={image.title}
          className="w-full h-96 md:h-[600px] object-cover rounded-2xl shadow-2xl"
        />

        {/* Text overlay that fades out during zoom */}
        <motion.div
          className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-black/80 to-transparent rounded-b-2xl"
          style={{ opacity: textOpacity, y: textY }}
        >
          <h3 className="text-3xl font-bold text-white mb-2">{image.title}</h3>
          <p className="text-white/80 text-lg">{image.description}</p>
        </motion.div>
      </motion.div>

      {/* Content that appears when image is zoomed */}
      <motion.div
        className="absolute inset-0 flex items-center justify-center p-8 pointer-events-none"
        style={{ opacity: contentOpacity, y: contentY }}
      >
        <div className="max-w-4xl w-full bg-white/10 backdrop-blur-xl rounded-2xl p-8 border border-white/20 pointer-events-auto">
          <motion.h2
            className="text-4xl md:text-5xl font-bold text-white mb-6 text-center"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
          >
            {image.title}
          </motion.h2>
          
          <motion.p
            className="text-xl text-white/80 mb-8 text-center leading-relaxed"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
          >
            {image.details}
          </motion.p>

          <motion.div
            className="grid md:grid-cols-2 gap-8 mb-8"
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
          >
            <div>
              <h4 className="text-2xl font-semibold text-white mb-4">Key Features</h4>
              <div className="space-y-3">
                {image.features.map((feature, idx) => (
                  <motion.div
                    key={feature}
                    className="flex items-center space-x-3"
                    initial={{ opacity: 0, x: -20 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.5 + idx * 0.1 }}
                  >
                    <div className="w-3 h-3 bg-blue-400 rounded-full"></div>
                    <span className="text-white/80">{feature}</span>
                  </motion.div>
                ))}
              </div>
            </div>
            
            <div className="flex items-center justify-center">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => navigate('/dashboard')}
                className="px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg hover:shadow-blue-500/25 transition-all duration-300"
              >
                Experience This Technology
              </motion.button>
            </div>
          </motion.div>
        </div>
      </motion.div>
    </div>
  );
};

export default LandingPage; 