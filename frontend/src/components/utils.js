// utils.js

export const handleChange = (setter, min, max) => (e) => {
    const value = Number(e.target.value);
    if (value >= min && value <= max) {
        setter(value);
    } else if (value > max) {
        setter(max);
    } else {
        setter(min);
    }
};
