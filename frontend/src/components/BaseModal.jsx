import "./BaseModal.css";

export default function BaseModal({ title, children, onClose, footer }) {
  return (
    <div className="base-modal-backdrop" onClick={onClose}>
      <div className="base-modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="base-modal-header">
          <h2>{title}</h2>
          <button className="base-modal-close" onClick={onClose}>&times;</button>
        </div>
        <div className="base-modal-body">
          {children}
        </div>
        {footer && (
          <div className="base-modal-footer">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
