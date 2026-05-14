import { useEffect, useRef } from "react";
import PropTypes from "prop-types";
import "./BaseModal.css";

export default function BaseModal({ title, children, onClose, footer }) {
  const dialogRef = useRef(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      dialog.showModal();
    }
  }, []);

  return (
    <dialog
      ref={dialogRef}
      className="base-modal-backdrop"
      onCancel={onClose}
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
