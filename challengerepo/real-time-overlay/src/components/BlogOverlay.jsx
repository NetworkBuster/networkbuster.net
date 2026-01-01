import { useState, useEffect } from 'react';
import { Calendar, Clock, User, Tag, ArrowRight, Search, TrendingUp, 
         MessageSquare, Heart, Share2, Bookmark, ChevronLeft, ChevronRight } from 'lucide-react';

// Featured post hero card
function FeaturedPost({ post }) {
    const [isHovered, setIsHovered] = useState(false);
    
    return (
        <div 
            className="relative h-[400px] rounded-2xl overflow-hidden group cursor-pointer"
            onMouseEnter={() => setIsHovered(true)}
            onMouseLeave={() => setIsHovered(false)}
        >
            {/* Background gradient animation */}
            <div className={`absolute inset-0 bg-gradient-to-br from-[#667eea] via-[#764ba2] to-[#ff003c] transition-all duration-700 ${isHovered ? 'scale-110' : 'scale-100'}`} />
            
            {/* Animated particles */}
            <div className="absolute inset-0 overflow-hidden">
                {[...Array(20)].map((_, i) => (
                    <div 
                        key={i}
                        className="absolute w-1 h-1 bg-white/30 rounded-full animate-pulse"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 2}s`,
                            animationDuration: `${2 + Math.random() * 2}s`
                        }}
                    />
                ))}
            </div>
            
            {/* Content overlay */}
            <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent" />
            
            {/* Badge */}
            <div className="absolute top-6 left-6">
                <span className="px-4 py-2 bg-[#00f0ff] text-black text-xs font-bold rounded-full uppercase tracking-wider">
                    Featured
                </span>
            </div>
            
            {/* Content */}
            <div className="absolute bottom-0 left-0 right-0 p-8">
                <div className="flex items-center gap-4 mb-4">
                    <span className="px-3 py-1 bg-white/10 backdrop-blur-sm rounded-full text-xs text-white/80">
                        {post.category}
                    </span>
                    <span className="text-white/60 text-sm flex items-center gap-1">
                        <Clock size={12} /> {post.readTime}
                    </span>
                </div>
                
                <h2 className={`text-3xl font-bold text-white mb-4 transition-transform duration-300 ${isHovered ? 'translate-x-2' : ''}`}>
                    {post.title}
                </h2>
                
                <p className="text-white/70 text-sm mb-6 line-clamp-2">
                    {post.excerpt}
                </p>
                
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-[#00f0ff] to-[#667eea] flex items-center justify-center text-white font-bold">
                            {post.author[0]}
                        </div>
                        <div>
                            <div className="text-white text-sm font-medium">{post.author}</div>
                            <div className="text-white/50 text-xs">{post.date}</div>
                        </div>
                    </div>
                    
                    <button className={`flex items-center gap-2 px-4 py-2 bg-white text-black rounded-full text-sm font-bold transition-all duration-300 ${isHovered ? 'translate-x-0 opacity-100' : '-translate-x-4 opacity-0'}`}>
                        Read More <ArrowRight size={14} />
                    </button>
                </div>
            </div>
        </div>
    );
}

// Blog post card with hover effects
function BlogCard({ post, variant = 'default' }) {
    const [liked, setLiked] = useState(false);
    const [saved, setSaved] = useState(false);
    
    if (variant === 'compact') {
        return (
            <div className="flex gap-4 p-4 bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl hover:border-[#00f0ff]/50 transition-all group cursor-pointer">
                <div className="w-20 h-20 rounded-lg bg-gradient-to-br from-[#667eea] to-[#764ba2] flex-shrink-0" />
                <div className="flex-1 min-w-0">
                    <span className="text-[10px] text-[#00f0ff] uppercase tracking-wider">{post.category}</span>
                    <h4 className="text-sm font-bold text-white group-hover:text-[#00f0ff] transition-colors line-clamp-2 mt-1">
                        {post.title}
                    </h4>
                    <div className="flex items-center gap-2 mt-2 text-[10px] text-white/50">
                        <span>{post.date}</span>
                        <span>•</span>
                        <span>{post.readTime}</span>
                    </div>
                </div>
            </div>
        );
    }
    
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl overflow-hidden hover:border-[#00f0ff]/50 transition-all group">
            {/* Image placeholder with gradient */}
            <div className="h-48 bg-gradient-to-br from-[#1a1a2e] to-[#16213e] relative overflow-hidden">
                <div className="absolute inset-0 bg-gradient-to-br from-[#667eea]/30 to-[#764ba2]/30 group-hover:scale-110 transition-transform duration-500" />
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="w-16 h-16 rounded-full bg-white/10 flex items-center justify-center">
                        <Tag size={24} className="text-white/40" />
                    </div>
                </div>
                {/* Category badge */}
                <div className="absolute top-4 left-4">
                    <span className="px-3 py-1 bg-[#00f0ff]/20 backdrop-blur-sm border border-[#00f0ff]/30 rounded-full text-[10px] text-[#00f0ff] uppercase tracking-wider">
                        {post.category}
                    </span>
                </div>
            </div>
            
            {/* Content */}
            <div className="p-5">
                <h3 className="text-lg font-bold text-white group-hover:text-[#00f0ff] transition-colors mb-2 line-clamp-2">
                    {post.title}
                </h3>
                <p className="text-sm text-white/60 mb-4 line-clamp-2">
                    {post.excerpt}
                </p>
                
                {/* Meta */}
                <div className="flex items-center justify-between text-xs text-white/50 mb-4">
                    <div className="flex items-center gap-2">
                        <User size={12} />
                        <span>{post.author}</span>
                    </div>
                    <div className="flex items-center gap-2">
                        <Calendar size={12} />
                        <span>{post.date}</span>
                    </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center justify-between pt-4 border-t border-white/10">
                    <div className="flex items-center gap-4">
                        <button 
                            onClick={() => setLiked(!liked)}
                            className={`flex items-center gap-1 text-xs transition-colors ${liked ? 'text-red-500' : 'text-white/50 hover:text-red-500'}`}
                        >
                            <Heart size={14} fill={liked ? 'currentColor' : 'none'} />
                            {post.likes}
                        </button>
                        <button className="flex items-center gap-1 text-xs text-white/50 hover:text-[#00f0ff] transition-colors">
                            <MessageSquare size={14} />
                            {post.comments}
                        </button>
                        <button className="flex items-center gap-1 text-xs text-white/50 hover:text-[#00f0ff] transition-colors">
                            <Share2 size={14} />
                        </button>
                    </div>
                    <button 
                        onClick={() => setSaved(!saved)}
                        className={`transition-colors ${saved ? 'text-[#00f0ff]' : 'text-white/50 hover:text-[#00f0ff]'}`}
                    >
                        <Bookmark size={14} fill={saved ? 'currentColor' : 'none'} />
                    </button>
                </div>
            </div>
        </div>
    );
}

// Category filter tabs
function CategoryTabs({ categories, active, onChange }) {
    return (
        <div className="flex gap-2 overflow-x-auto pb-2 custom-scrollbar">
            {categories.map((cat) => (
                <button
                    key={cat}
                    onClick={() => onChange(cat)}
                    className={`px-4 py-2 rounded-full text-xs font-bold whitespace-nowrap transition-all ${
                        active === cat
                            ? 'bg-[#00f0ff] text-black'
                            : 'bg-white/5 text-white/60 hover:bg-white/10 hover:text-white'
                    }`}
                >
                    {cat}
                </button>
            ))}
        </div>
    );
}

// Trending topics sidebar
function TrendingTopics({ topics }) {
    return (
        <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-5">
            <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp size={14} className="text-[#ff003c]" />
                TRENDING TOPICS
            </h3>
            <div className="space-y-3">
                {topics.map((topic, i) => (
                    <div key={i} className="flex items-center gap-3 group cursor-pointer">
                        <span className="text-2xl font-bold text-white/20 group-hover:text-[#00f0ff]/50 transition-colors">
                            {String(i + 1).padStart(2, '0')}
                        </span>
                        <div>
                            <div className="text-sm text-white group-hover:text-[#00f0ff] transition-colors">
                                {topic.name}
                            </div>
                            <div className="text-[10px] text-white/40">{topic.posts} posts</div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}

export default function BlogOverlay() {
    const [activeCategory, setActiveCategory] = useState('All');
    const [searchQuery, setSearchQuery] = useState('');
    
    const categories = ['All', 'Technology', 'Space', 'AI/ML', 'Networking', 'Tutorials'];
    
    const featuredPost = {
        title: 'Building the Future of Lunar Communications',
        excerpt: 'Exploring the challenges and innovations in establishing reliable communication networks on the Moon. From laser relay systems to quantum-encrypted channels.',
        category: 'Space Technology',
        author: 'Dr. Sarah Chen',
        date: 'Jan 1, 2026',
        readTime: '8 min read'
    };
    
    const posts = [
        { title: 'Real-Time Data Visualization with Three.js', excerpt: 'Create stunning 3D visualizations for your data dashboards using React Three Fiber.', category: 'Tutorials', author: 'Alex Morgan', date: 'Dec 28, 2025', readTime: '5 min', likes: 142, comments: 23 },
        { title: 'Quantum Networking: A Primer', excerpt: 'Understanding the fundamentals of quantum entanglement for secure communications.', category: 'Technology', author: 'Dr. James Lee', date: 'Dec 25, 2025', readTime: '12 min', likes: 89, comments: 15 },
        { title: 'Deploying AI Models at the Edge', excerpt: 'Best practices for running machine learning inference on resource-constrained devices.', category: 'AI/ML', author: 'Maria Garcia', date: 'Dec 22, 2025', readTime: '7 min', likes: 234, comments: 41 },
        { title: 'The NetworkBuster Architecture Deep Dive', excerpt: 'An inside look at how we built our distributed system for lunar operations.', category: 'Networking', author: 'Core Team', date: 'Dec 20, 2025', readTime: '15 min', likes: 312, comments: 67 },
        { title: 'Space-Grade Hardware Testing', excerpt: 'How we validate our equipment for the harsh conditions of space.', category: 'Space', author: 'Engineering Team', date: 'Dec 18, 2025', readTime: '6 min', likes: 178, comments: 29 },
        { title: 'Building Resilient Microservices', excerpt: 'Patterns and practices for fault-tolerant distributed systems.', category: 'Technology', author: 'Alex Morgan', date: 'Dec 15, 2025', readTime: '9 min', likes: 156, comments: 34 },
    ];
    
    const trendingTopics = [
        { name: '#LunarNetwork', posts: 1234 },
        { name: '#QuantumComputing', posts: 892 },
        { name: '#SpaceTech2026', posts: 756 },
        { name: '#EdgeAI', posts: 623 },
        { name: '#NetworkBuster', posts: 512 },
    ];
    
    const recentPosts = posts.slice(0, 4);
    
    return (
        <div className="w-full h-full p-6 overflow-auto custom-scrollbar">
            {/* Header */}
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white">
                        Network<span className="text-[#00f0ff]">Blog</span>
                    </h1>
                    <p className="text-white/50 text-sm mt-1">Insights from the frontier of space networking</p>
                </div>
                
                {/* Search */}
                <div className="relative">
                    <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
                    <input
                        type="text"
                        placeholder="Search articles..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-64 pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-full text-sm text-white placeholder:text-white/40 focus:outline-none focus:border-[#00f0ff]/50"
                    />
                </div>
            </div>
            
            {/* Category Tabs */}
            <div className="mb-8">
                <CategoryTabs categories={categories} active={activeCategory} onChange={setActiveCategory} />
            </div>
            
            {/* Main Content Grid */}
            <div className="grid grid-cols-12 gap-6">
                {/* Main Content */}
                <div className="col-span-8 space-y-6">
                    {/* Featured Post */}
                    <FeaturedPost post={featuredPost} />
                    
                    {/* Posts Grid */}
                    <div className="grid grid-cols-2 gap-4">
                        {posts.map((post, i) => (
                            <BlogCard key={i} post={post} />
                        ))}
                    </div>
                    
                    {/* Pagination */}
                    <div className="flex items-center justify-center gap-2 pt-6">
                        <button className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                            <ChevronLeft size={16} className="text-white/60" />
                        </button>
                        {[1, 2, 3, 4, 5].map((page) => (
                            <button
                                key={page}
                                className={`w-8 h-8 rounded-lg text-sm font-bold transition-colors ${
                                    page === 1 ? 'bg-[#00f0ff] text-black' : 'bg-white/5 text-white/60 hover:bg-white/10'
                                }`}
                            >
                                {page}
                            </button>
                        ))}
                        <button className="p-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                            <ChevronRight size={16} className="text-white/60" />
                        </button>
                    </div>
                </div>
                
                {/* Sidebar */}
                <div className="col-span-4 space-y-6">
                    {/* Trending Topics */}
                    <TrendingTopics topics={trendingTopics} />
                    
                    {/* Recent Posts */}
                    <div className="bg-black/40 backdrop-blur-sm border border-white/10 rounded-xl p-5">
                        <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2">
                            <Clock size={14} className="text-[#00f0ff]" />
                            RECENT POSTS
                        </h3>
                        <div className="space-y-3">
                            {recentPosts.map((post, i) => (
                                <BlogCard key={i} post={post} variant="compact" />
                            ))}
                        </div>
                    </div>
                    
                    {/* Newsletter */}
                    <div className="bg-gradient-to-br from-[#667eea]/20 to-[#764ba2]/20 border border-[#667eea]/30 rounded-xl p-5">
                        <h3 className="text-sm font-bold text-white mb-2">Stay Updated</h3>
                        <p className="text-xs text-white/60 mb-4">Get the latest articles delivered to your inbox.</p>
                        <input
                            type="email"
                            placeholder="Enter your email"
                            className="w-full px-4 py-2 bg-black/40 border border-white/10 rounded-lg text-sm text-white placeholder:text-white/40 focus:outline-none focus:border-[#667eea]/50 mb-3"
                        />
                        <button className="w-full py-2 bg-[#667eea] text-white text-sm font-bold rounded-lg hover:bg-[#764ba2] transition-colors">
                            Subscribe
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
