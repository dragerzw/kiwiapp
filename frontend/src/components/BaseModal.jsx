import PropTypes from "prop-types";
import "./BaseModal.css";

export default function BaseModal({ title, children, onClose, footer }) {
  return (
    <dialog
      className="base-modal-backdrop"
      onCancel={onClose}
      open
    >
      <div className="base-modal-content" aria-label={title}>
        <div className="base-modal-header">
          <h2>{title}</h2>
          <button className="base-modal-close" onClick={onClose} type="button" aria-label="Close modal">&times;</button>
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
    </dialog>
  );
}

BaseModal.propTypes = {
  title: PropTypes.string.isRequired,
  children: PropTypes.node.isRequired,
  onClose: PropTypes.func.isRequired,
  footer: PropTypes.node,
};
