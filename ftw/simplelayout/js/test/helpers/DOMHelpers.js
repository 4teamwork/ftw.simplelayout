require('babelify-es6-polyfill');

export function getNodeAttributesAsObject(node) {
  const attributesMap = node.attributes;
  let attributesObject = {};
  Array.from(attributesMap).forEach((item) => {
    attributesObject[item.name] = item.value;
  });
  return attributesObject;
}
