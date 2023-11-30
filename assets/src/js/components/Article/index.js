// src/components/Article.js
import React, { useState } from 'react';

const Article = ({ title, content }) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleArticle = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="article">
      <button onClick={toggleArticle}>
        {isOpen ? 'Fechar Seção: ' : 'Ler Seção: '}
        {title}
      </button>
      {isOpen && <p>{content}</p>}
    </div>
  );
};

export default Article;
