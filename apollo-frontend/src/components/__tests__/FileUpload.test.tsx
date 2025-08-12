import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import FileUpload from '../Upload/FileUpload';

// Mock dependencies
jest.mock('react-hot-toast');
jest.mock('../../services/api', () => ({
  uploadFile: jest.fn()
}));

const mockNavigate = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('FileUpload Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload area', () => {
    renderWithRouter(<FileUpload />);
    
    expect(screen.getByText(/drag and drop/i)).toBeInTheDocument();
    expect(screen.getByText(/or click to browse/i)).toBeInTheDocument();
  });

  it('shows supported file types', () => {
    renderWithRouter(<FileUpload />);
    
    expect(screen.getByText(/CSV, XLS, XLSX/i)).toBeInTheDocument();
  });

  it('handles file selection', async () => {
    const file = new File(['test data'], 'test.csv', { type: 'text/csv' });
    
    renderWithRouter(<FileUpload />);
    
    const input = screen.getByTestId('file-input');
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(screen.getByText('test.csv')).toBeInTheDocument();
    });
  });

  it('validates file type', async () => {
    const file = new File(['test data'], 'test.txt', { type: 'text/plain' });
    
    renderWithRouter(<FileUpload />);
    
    const input = screen.getByTestId('file-input');
    fireEvent.change(input, { target: { files: [file] } });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('File type not supported')
      );
    });
  });

  it('validates file size', async () => {
    // Create a large file (over 10MB)
    const largeFile = new File(['x'.repeat(11 * 1024 * 1024)], 'large.csv', { 
      type: 'text/csv' 
    });
    
    renderWithRouter(<FileUpload />);
    
    const input = screen.getByTestId('file-input');
    fireEvent.change(input, { target: { files: [largeFile] } });
    
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('File too large')
      );
    });
  });
}); 