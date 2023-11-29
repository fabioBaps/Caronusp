// src/components/Articles.js
import React from 'react';
import Article from '../Article';

const Articles = ({ articles, selectedArticle, onToggleArticle }) => {
  return (
    <div className="articles">
      {articles.map((article) => (
        <Article
          key={article.id}
          title={article.title}
          content={article.content}
          isOpen={selectedArticle === article.id}
          onToggle={() => onToggleArticle(article.id)}
        />
      ))}
    </div>
  );
};

export default Articles;
