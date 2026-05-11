import PortfolioCard from "./PortfolioCard";

const PortfolioList = ({ portfolios, onDeleteError, onDeleteSuccess, onSelect }) => {
  if (portfolios.length === 0) {
    return (
      <div className="empty-state">
        <h3>No portfolios yet</h3>
        <p>Create your first portfolio to start tracking investments and trade history.</p>
      </div>
    );
  }

  return (
    <div className="portfolio-grid">
      {portfolios.map((portfolio) => (
        <PortfolioCard
          key={portfolio.id}
          onDeleteError={onDeleteError}
          onDeleteSuccess={onDeleteSuccess}
          onSelect={onSelect}
          portfolio={portfolio}
        />
      ))}
    </div>
  );
};

export default PortfolioList;
