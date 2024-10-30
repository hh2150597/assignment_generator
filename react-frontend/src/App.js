import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [formData, setFormData] = useState({
    topic: '',
    bookName: '',
    reference: '',
    authorName: '',
    category: '',
    bookType: '',
    description: ''
  });
  const [pdfCreated, setPdfCreated] = useState(false);
  const [pdfUrl, setPdfUrl] = useState(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsGenerating(true);
    try {
      const response = await axios.post('http://localhost:8000/api/generate-pdf/', formData, {
        responseType: 'blob' // important to receive file
      });
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      setPdfUrl(url);
      setPdfCreated(true);
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Book not found or an error occurred');
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    const link = document.createElement('a');
    link.href = pdfUrl;
    link.setAttribute('download', 'generated_assignment.pdf');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    resetForm();
  };

  const resetForm = () => {
    setFormData({
      topic: '',
      bookName: '',
      reference: '',
      authorName: '',
      category: '',
      bookType: '',
      description: ''
    });
    setPdfUrl(null);
    setPdfCreated(false);
  };

  return (
    <div className="App container mt-5">
      <h1 className="text-center mb-4 text-secondary">Assignment PDF Generator</h1>
      <form onSubmit={handleSubmit} className='pb-2'>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Topic:</label>
            <input
              type="text"
              name="topic"
              value={formData.topic}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
          <div className="col-md-6">
            <label className="form-label">Book Name:</label>
            <input
              type="text"
              name="bookName"
              value={formData.bookName}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Reference:</label>
            <input
              type="text"
              name="reference"
              value={formData.reference}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
          <div className="col-md-6">
            <label className="form-label">Author Name:</label>
            <input
              type="text"
              name="authorName"
              value={formData.authorName}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
        </div>
        <div className="row mb-3">
          <div className="col-md-6">
            <label className="form-label">Category:</label>
            <input
              type="text"
              name="category"
              value={formData.category}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
          <div className="col-md-6">
            <label className="form-label">Book Type:</label>
            <input
              type="text"
              name="bookType"
              value={formData.bookType}
              onChange={handleChange}
              className="form-control border border-secondary"
              required
            />
          </div>
        </div>
        <div className="mb-3">
          <label className="form-label">Description:</label>
          <textarea
            name="description"
            value={formData.description}
            onChange={handleChange}
            className="form-control border border-secondary"
            rows="4"
            required
          />
        </div>
        <div className="text-center">
          <button type="submit" className="btn btn-secondary">
            {isGenerating ? 'Generating...' : 'Generate PDF'}
          </button>
        </div>
      </form>

      {pdfCreated && (
        <div className="card mt-4 mb-4 border border-secondary">
          <div className="card-body text-center">
            <h5 className="card-title">PDF Created</h5>
            <p className="card-text">Your PDF has been successfully created. Do you want to download it?</p>
            <button onClick={handleDownload} className="btn btn-success me-2">Download</button>
            <button onClick={resetForm} className="btn btn-secondary">Cancel</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
