import { Fragment, isValidElement, type ReactElement, type ReactNode } from 'react';

// Emails are static HTML, so they are rendered here without react-dom/server: route handlers run on
// React's server build, which react-dom/server can't use, and this keeps the edge bundle small.
// It supports what email templates need: host elements, function and forwardRef components,
// fragments, style objects and dangerouslySetInnerHTML. Hooks and context are not available.
// Text and attribute values are always escaped; only dangerouslySetInnerHTML passes through raw,
// so never feed it visitor input.

const DOCTYPE =
  '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">';

const VOID_TAGS = new Set([
  'area',
  'base',
  'br',
  'col',
  'embed',
  'hr',
  'img',
  'input',
  'link',
  'meta',
  'source',
  'wbr',
]);
// CSS properties that take plain numbers, as in React.
const UNITLESS = new Set([
  'flex',
  'flexGrow',
  'flexShrink',
  'fontWeight',
  'lineHeight',
  'opacity',
  'order',
  'zIndex',
  'zoom',
]);
const ATTRIBUTE_NAMES: Record<string, string> = { className: 'class', htmlFor: 'for', httpEquiv: 'http-equiv' };
const FORWARD_REF = Symbol.for('react.forward_ref');
const MEMO = Symbol.for('react.memo');

const escapeText = (value: string) => value.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
const escapeAttribute = (value: string) => escapeText(value).replace(/"/g, '&quot;');

const styleToCss = (style: Record<string, unknown>) =>
  Object.entries(style)
    .filter(([, value]) => value !== null && value !== undefined && value !== '')
    .map(([key, value]) => {
      const property = key.replace(/[A-Z]/g, (c) => `-${c.toLowerCase()}`);
      const css = typeof value === 'number' && value !== 0 && !UNITLESS.has(key) ? `${value}px` : String(value);
      return `${property}:${css}`;
    })
    .join(';');

const renderAttributes = (props: Record<string, unknown>) =>
  Object.entries(props)
    .filter(([key, value]) => {
      if (['children', 'key', 'ref', 'dangerouslySetInnerHTML'].includes(key)) return false;
      return value !== null && value !== undefined && value !== false && typeof value !== 'function';
    })
    .map(([key, value]) => {
      const name =
        ATTRIBUTE_NAMES[key] ?? (key.startsWith('data-') || key.startsWith('aria-') ? key : key.toLowerCase());
      const text = key === 'style' ? styleToCss(value as Record<string, unknown>) : value === true ? '' : String(value);
      return ` ${name}="${escapeAttribute(text)}"`;
    })
    .join('');

const renderNode = (node: ReactNode): string => {
  if (node === null || node === undefined || typeof node === 'boolean') return '';
  if (typeof node === 'string' || typeof node === 'number' || typeof node === 'bigint') return escapeText(String(node));
  if (Array.isArray(node)) return node.map(renderNode).join('');
  if (!isValidElement(node)) return '';

  const { type } = node;
  const props = node.props as Record<string, unknown>;

  if (type === Fragment) return renderNode(props.children as ReactNode);
  if (typeof type === 'function') return renderNode((type as (p: unknown) => ReactNode)(props));
  if (typeof type === 'object' && type !== null) {
    const special = type as { $$typeof?: symbol; render?: (p: unknown, ref: null) => ReactNode; type?: unknown };
    if (special.$$typeof === FORWARD_REF && special.render) return renderNode(special.render(props, null));
    if (special.$$typeof === MEMO) return renderNode({ ...node, type: special.type } as ReactElement);
  }
  if (typeof type !== 'string') return '';

  const attributes = renderAttributes(props);
  if (VOID_TAGS.has(type)) return `<${type}${attributes} />`;
  const inner = props.dangerouslySetInnerHTML as { __html?: string } | undefined;
  const children = inner?.__html ?? renderNode(props.children as ReactNode);
  return `<${type}${attributes}>${children}</${type}>`;
};

/** A React Email template as a complete HTML document. */
export const renderEmail = (email: ReactElement) => DOCTYPE + renderNode(email);
