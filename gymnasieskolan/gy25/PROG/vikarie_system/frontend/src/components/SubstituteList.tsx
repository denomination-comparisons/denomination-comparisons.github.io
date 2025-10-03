import React, { useEffect, useState } from 'react';
import { Substitute } from '../types';
import { getSubstitutes } from '../services/api';

const SubstituteList: React.FC = () => {
  const [substitutes, setSubstitutes] = useState<Substitute[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSubstitutes = async () => {
      try {
        const data = await getSubstitutes();
        setSubstitutes(data);
      } catch (error) {
        console.error('Error fetching substitutes:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchSubstitutes();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Substitutes</h2>
      <ul>
        {substitutes.map((sub) => (
          <li key={sub.id}>
            {sub.name} - {sub.email} - Rating: {sub.reliability_rating}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default SubstituteList;
