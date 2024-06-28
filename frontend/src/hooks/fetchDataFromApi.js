import axios from 'axios';

const fetchDataFromApi = async (url) => {
  try {
    const response = await axios.get(`${process.env.REACT_APP_API_URL}/${url}`);
    return response.data;
  } catch (error) {
    throw new Error(error.message);
  }
};

export default fetchDataFromApi;
