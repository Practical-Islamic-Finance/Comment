module.exports = {
  plugins: [
    require('postcss-prefix-selector')({
      prefix: '.comments-section', // This will be added before all your selectors
      transform: function (prefix, selector, prefixedSelector) {
        // If the selector is for the html or body tag, it leaves the selector without prefixing
        if (selector === 'html' || selector === 'body') {
          return selector;
        }
        // If the selector already has `.comments-section`, it should not duplicate the prefix
        if (selector.startsWith('.comments-section')) {
          return selector;
        }
        // This is to prevent over-qualification of selectors which can make them too specific
        if (selector.startsWith('.')) {
          return prefix + ' ' + selector;
        }
        // In case of other selectors, just add the prefix as normal
        return prefixedSelector;
      }
    })
  ]
};
