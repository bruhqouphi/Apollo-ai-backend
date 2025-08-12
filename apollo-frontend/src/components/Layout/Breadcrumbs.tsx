import React from 'react';
import { motion } from 'framer-motion';
import { ChevronRight, Home } from 'lucide-react';
import { useLocation, Link } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path: string;
  isActive?: boolean;
}

const Breadcrumbs: React.FC = () => {
  const location = useLocation();
  
  const getBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Home', path: '/', isActive: location.pathname === '/' }
    ];
    
    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({
        label,
        path: currentPath,
        isActive: index === pathSegments.length - 1
      });
    });
    
    return breadcrumbs;
  };

  const breadcrumbs = getBreadcrumbs();

  if (breadcrumbs.length <= 1) {
    return null;
  }

  return (
    <motion.nav
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center space-x-2 text-sm mb-6"
      aria-label="Breadcrumb"
    >
      {breadcrumbs.map((item, index) => (
        <React.Fragment key={item.path}>
          {index > 0 && (
            <ChevronRight className="w-4 h-4 text-white/40" />
          )}
          {item.isActive ? (
            <span className="text-white font-medium" aria-current="page">
              {index === 0 ? <Home className="w-4 h-4 inline mr-1" /> : null}
              {item.label}
            </span>
          ) : (
            <Link
              to={item.path}
              className="text-white/60 hover:text-white transition-colors flex items-center"
            >
              {index === 0 ? <Home className="w-4 h-4 mr-1" /> : null}
              {item.label}
            </Link>
          )}
        </React.Fragment>
      ))}
    </motion.nav>
  );
};

export default Breadcrumbs; 