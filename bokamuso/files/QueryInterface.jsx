/**
 * QueryInterface Component
 * Main interface for asking questions
 */
import React, { useState } from 'react';
import { useSubjects, useQuery, useFeedback } from '../hooks/useRAG';
import './QueryInterface.css';

function QueryInterface() {
  const { subjects, loading: subjectsLoading } = useSubjects();
  const { askQuestion, loading: queryLoading, result, error: queryError } = useQuery();
  const { submitFeedback, submitting: feedbackSubmitting } = useFeedback();

  const [selectedSubject, setSelectedSubject] = useState('');
  const [queryText, setQueryText] = useState('');
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedSubject || !queryText.trim()) {
      alert('Please select a subject and enter a question');
      return;
    }

    try {
      await askQuestion(selectedSubject, queryText);
      setShowFeedback(false);
    } catch (error) {
      console.error('Query failed:', error);
    }
  };

  const handleFeedbackSubmit = async (e) => {
    e.preventDefault();
    
    if (!feedbackRating) {
      alert('Please select a rating');
      return;
    }

    try {
      await submitFeedback(result.query_id, feedbackRating, feedbackComment);
      alert('Thank you for your feedback!');
      setShowFeedback(false);
      setFeedbackRating(0);
      setFeedbackComment('');
    } catch (error) {
      console.error('Feedback submission failed:', error);
    }
  };

  const handleFollowUpClick = (question) => {
    setQueryText(question);
  };

  return (
    <div className="query-interface">
      <div className="query-form-container">
        <h2>Ask a Question</h2>
        
        <form onSubmit={handleSubmit} className="query-form">
          <div className="form-group">
            <label htmlFor="subject">Subject:</label>
            <select
              id="subject"
              value={selectedSubject}
              onChange={(e) => setSelectedSubject(e.target.value)}
              disabled={subjectsLoading || queryLoading}
              required
            >
              <option value="">Select a subject</option>
              {subjects.map((subject) => (
                <option key={subject.id} value={subject.name}>
                  {subject.display_name}
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="query">Your Question:</label>
            <textarea
              id="query"
              value={queryText}
              onChange={(e) => setQueryText(e.target.value)}
              placeholder="Enter your question here..."
              rows="4"
              disabled={queryLoading}
              required
            />
          </div>

          <button 
            type="submit" 
            className="submit-btn"
            disabled={queryLoading || !selectedSubject}
          >
            {queryLoading ? 'Processing...' : 'Ask Question'}
          </button>
        </form>
      </div>

      {queryError && (
        <div className="error-message">
          <strong>Error:</strong> {queryError}
        </div>
      )}

      {result && (
        <div className="result-container">
          <div className="answer-section">
            <h3>Answer:</h3>
            <div className="answer-content">
              {result.answer}
            </div>

            <div className="answer-metadata">
              <span>Tokens used: {result.tokens_used}</span>
              <span>Sources: {result.sources.length}</span>
            </div>
          </div>

          {result.sources && result.sources.length > 0 && (
            <div className="sources-section">
              <h4>Sources:</h4>
              <ul className="sources-list">
                {result.sources.map((source, index) => (
                  <li key={index}>
                    <strong>{source.source}</strong> (Relevance: {source.score.toFixed(3)})
                  </li>
                ))}
              </ul>
            </div>
          )}

          {result.follow_up_questions && result.follow_up_questions.length > 0 && (
            <div className="follow-up-section">
              <h4>Follow-up Questions:</h4>
              <ul className="follow-up-list">
                {result.follow_up_questions.map((question, index) => (
                  <li key={index}>
                    <button
                      className="follow-up-btn"
                      onClick={() => handleFollowUpClick(question)}
                    >
                      {question}
                    </button>
                  </li>
                ))}
              </ul>
            </div>
          )}

          <div className="feedback-section">
            {!showFeedback ? (
              <button 
                className="feedback-toggle-btn"
                onClick={() => setShowFeedback(true)}
              >
                Rate this answer
              </button>
            ) : (
              <form onSubmit={handleFeedbackSubmit} className="feedback-form">
                <h4>How helpful was this answer?</h4>
                
                <div className="rating-stars">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      type="button"
                      className={`star ${feedbackRating >= star ? 'active' : ''}`}
                      onClick={() => setFeedbackRating(star)}
                    >
                      ★
                    </button>
                  ))}
                </div>

                <textarea
                  value={feedbackComment}
                  onChange={(e) => setFeedbackComment(e.target.value)}
                  placeholder="Additional comments (optional)"
                  rows="3"
                />

                <div className="feedback-actions">
                  <button 
                    type="submit" 
                    disabled={feedbackSubmitting || !feedbackRating}
                  >
                    {feedbackSubmitting ? 'Submitting...' : 'Submit Feedback'}
                  </button>
                  <button 
                    type="button"
                    onClick={() => setShowFeedback(false)}
                  >
                    Cancel
                  </button>
                </div>
              </form>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default QueryInterface;
