import React from 'react';
import Header from '../../header/Header';
import Footer from '../../footer/Footer';
import Heading from '../Heading';
import Tile from '../Tile';
import Pets from '../assets/pets.jpg';
import Food from '../assets/pet_food.jpg';
import Toys from '../assets/pet_toys.jpg';
import Groom from '../assets/pet_groom.jpg';
import './Home.css';

export default function Home() {
    return (
        <div className="home">
            <Header />
            <Heading
                imgSrc={Pets}
                title="Welcome to Pet Shop"
                description="Discover a world of love and care for your pets. From nutritious food to fun toys and essential grooming supplies, we have everything your furry, feathered, or scaly friends need to live their best life."
            />
            <div className="container">
                <div className="tiles">
                    <Tile
                        imgSrc={Food}
                        title="Premium Pet Food"
                        description="Keep your furry friends healthy and happy with our wide selection of nutritious and delicious pet food."
                    />
                    <Tile
                        imgSrc={Toys}
                        title="Toys & Accessories"
                        description="Explore fun toys and handy accessories that your pets will love. From squeaky toys to cozy beds, we have it all."
                    />
                    <Tile
                        imgSrc={Groom}
                        title="Pet Grooming"
                        description="Pamper your pets with our top-quality grooming products to keep them looking and feeling their best."
                    />
                </div>
                <button className="view-more">View More</button>
            </div>
            <Footer />
        </div>
    );
}