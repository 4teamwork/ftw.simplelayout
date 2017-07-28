import $ from "jquery";

export function getNodeAttributesAsObject(node) {
  const attributesMap = node.attributes;
  const attributesObject = {};
  $.each(attributesMap, (i, e) => {
    attributesObject[e.name] = e.value;
  });
  return attributesObject;
}
