import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Clock, TrendingUp, FileText, BarChart3, Brain } from 'lucide-react';
import { useAppStore } from '../../store/useAppStore';

interface SearchResult {
  id: string;
  type: 'file' | 'analysis' | 'chart' | 'insight';
  title: string;
  description: string;
  icon: React.ReactNode;
  path: string;
}

interface SearchBarProps {
  onSearch: (query: string) => void;
  onResultSelect: (result: SearchResult) => void;
}

const SearchBar: React.FC<SearchBarProps> = ({ onSearch, onResultSelect }) => {
  const [query, setQuery] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const [recentSearches, setRecentSearches] = useState<string[]>([]);
  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const searchRef = useRef<HTMLDivElement>(null);
  const { uploadedFiles, analysisResult, insights, chartGallery } = useAppStore();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  useEffect(() => {
    // Load recent searches from localStorage
    const saved = localStorage.getItem('apollo-recent-searches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
  }, []);

  const saveRecentSearch = (search: string) => {
    const updated = [search, ...recentSearches.filter(s => s !== search)].slice(0, 5);
    setRecentSearches(updated);
    localStorage.setItem('apollo-recent-searches', JSON.stringify(updated));
  };

  const handleSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      return;
    }

    setIsLoading(true);
    saveRecentSearch(searchQuery);

    const results: SearchResult[] = [];
    const lowerQuery = searchQuery.toLowerCase();

    // Search uploaded files
    uploadedFiles.forEach((file) => {
      if (file.filename.toLowerCase().includes(lowerQuery) ||
          file.columns.some(col => col.toLowerCase().includes(lowerQuery))) {
        results.push({
          id: `file-${file.file_id}`,
          type: 'file',
          title: file.filename,
          description: `${file.rows_count} rows, ${file.columns_count} columns`,
          icon: <FileText className="w-4 h-4" />,
          path: '/upload'
        });
      }
    });

    // Search analysis results
    if (analysisResult && (
      analysisResult.file_id.includes(lowerQuery) ||
      analysisResult.message.toLowerCase().includes(lowerQuery) ||
      JSON.stringify(analysisResult.analysis_results).toLowerCase().includes(lowerQuery)
    )) {
      results.push({
        id: `analysis-${analysisResult.file_id}`,
        type: 'analysis',
        title: 'Data Analysis Results',
        description: `Analysis completed in ${analysisResult.processing_time_seconds}s`,
        icon: <BarChart3 className="w-4 h-4" />,
        path: '/analysis'
      });
    }

    // Search insights
    if (insights && (
      insights.insights.executive_summary.toLowerCase().includes(lowerQuery) ||
      insights.insights.key_findings.some(finding => finding.toLowerCase().includes(lowerQuery)) ||
      insights.insights.recommendations.some(rec => rec.toLowerCase().includes(lowerQuery))
    )) {
      results.push({
        id: `insights-${insights.file_id}`,
        type: 'insight',
        title: 'AI Insights',
        description: 'AI-generated insights and recommendations',
        icon: <Brain className="w-4 h-4" />,
        path: '/insights'
      });
    }

    // Search charts
    chartGallery.forEach((chart) => {
      if (chart.chart_type.toLowerCase().includes(lowerQuery) ||
          chart.message.toLowerCase().includes(lowerQuery)) {
        results.push({
          id: `chart-${chart.file_id}-${chart.chart_type}`,
          type: 'chart',
          title: `${chart.chart_type} Chart`,
          description: chart.message,
          icon: <BarChart3 className="w-4 h-4" />,
          path: '/charts'
        });
      }
    });

    // Add static navigation results if no data matches
    if (results.length === 0) {
      const staticResults = [
        {
          id: 'nav-upload',
          type: 'file' as const,
          title: 'Upload Data',
          description: 'Upload CSV files for analysis',
          icon: <FileText className="w-4 h-4" />,
          path: '/upload'
        },
        {
          id: 'nav-analysis',
          type: 'analysis' as const,
          title: 'Data Analysis',
          description: 'Perform statistical analysis',
          icon: <BarChart3 className="w-4 h-4" />,
          path: '/analysis'
        },
        {
          id: 'nav-charts',
          type: 'chart' as const,
          title: 'Visualizations',
          description: 'Create charts and graphs',
          icon: <TrendingUp className="w-4 h-4" />,
          path: '/charts'
        },
        {
          id: 'nav-insights',
          type: 'insight' as const,
          title: 'AI Insights',
          description: 'Get AI-powered recommendations',
          icon: <Brain className="w-4 h-4" />,
          path: '/insights'
        }
      ].filter(result => 
        result.title.toLowerCase().includes(lowerQuery) ||
        result.description.toLowerCase().includes(lowerQuery)
      );
      results.push(...staticResults);
    }

    setSearchResults(results);
    setIsLoading(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    setIsOpen(true);
    
    if (value.trim()) {
      handleSearch(value);
    } else {
      setSearchResults([]);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    onResultSelect(result);
    setIsOpen(false);
    setQuery('');
  };

  const clearSearch = () => {
    setQuery('');
    setSearchResults([]);
    setIsOpen(false);
  };

  const getTypeColor = (type: SearchResult['type']) => {
    switch (type) {
      case 'file': return 'text-blue-400';
      case 'analysis': return 'text-green-400';
      case 'chart': return 'text-purple-400';
      case 'insight': return 'text-orange-400';
      default: return 'text-white/60';
    }
  };

  return (
    <div className="relative" ref={searchRef}>
      {/* Search Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/60" />
        <input
          type="text"
          value={query}
          onChange={handleInputChange}
          onFocus={() => setIsOpen(true)}
          placeholder="Search files, analyses, charts..."
          className="w-full pl-10 pr-10 py-2 bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 text-white placeholder-white/50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500/50 transition-all"
        />
        {query && (
          <button
            onClick={clearSearch}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 p-1 hover:bg-white/10 rounded transition-colors"
          >
            <X className="w-4 h-4 text-white/60" />
          </button>
        )}
      </div>

      {/* Search Results Dropdown */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: -10, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.95 }}
            className="absolute top-full mt-2 w-full glass-card rounded-xl border border-white/20 shadow-xl z-50 max-h-96 overflow-hidden"
          >
            {/* Loading State */}
            {isLoading && (
              <div className="p-4 text-center">
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-white/60 text-sm mt-2">Searching...</p>
              </div>
            )}

            {/* Search Results */}
            {!isLoading && searchResults.length > 0 && (
              <div className="p-2">
                <div className="text-xs text-white/40 px-3 py-2 font-medium">Search Results</div>
                {searchResults.map((result) => (
                  <button
                    key={result.id}
                    onClick={() => handleResultClick(result)}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                  >
                    <div className={`${getTypeColor(result.type)}`}>
                      {result.icon}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-white text-sm font-medium truncate">{result.title}</div>
                      <div className="text-white/60 text-xs truncate">{result.description}</div>
                    </div>
                  </button>
                ))}
              </div>
            )}

            {/* Recent Searches */}
            {!isLoading && searchResults.length === 0 && recentSearches.length > 0 && (
              <div className="p-2">
                <div className="text-xs text-white/40 px-3 py-2 font-medium">Recent Searches</div>
                {recentSearches.map((search, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setQuery(search);
                      handleSearch(search);
                    }}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                  >
                    <Clock className="w-4 h-4 text-white/40" />
                    <span className="text-white text-sm">{search}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Popular Searches */}
            {!isLoading && searchResults.length === 0 && recentSearches.length === 0 && (
              <div className="p-2">
                <div className="text-xs text-white/40 px-3 py-2 font-medium">Popular Searches</div>
                {['Sales Analysis', 'Customer Data', 'Revenue Trends', 'Market Insights'].map((search, index) => (
                  <button
                    key={index}
                    onClick={() => {
                      setQuery(search);
                      handleSearch(search);
                    }}
                    className="w-full flex items-center space-x-3 px-3 py-2 rounded-lg hover:bg-white/10 transition-colors text-left"
                  >
                    <TrendingUp className="w-4 h-4 text-white/40" />
                    <span className="text-white text-sm">{search}</span>
                  </button>
                ))}
              </div>
            )}

            {/* No Results */}
            {!isLoading && query && searchResults.length === 0 && (
              <div className="p-4 text-center">
                <Search className="w-8 h-8 text-white/40 mx-auto mb-2" />
                <p className="text-white/60 text-sm">No results found for "{query}"</p>
                <p className="text-white/40 text-xs mt-1">Try different keywords</p>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchBar; 