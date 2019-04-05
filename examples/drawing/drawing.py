from __future__ import unicode_literals


def main(debug=False):

    from textx import metamodel_from_str, get_children_of_type

    grammar = """
    Model: commands*=DrawCommand;
    DrawCommand: MoveCommand | ShapeCommand;
    ShapeCommand: LineTo | Circle;
    MoveCommand: MoveTo | MoveBy;
    MoveTo: 'move' 'to' position=Point;
    MoveBy: 'move' 'by' vector=Point;
    Circle: 'circle' radius=INT;
    LineTo: 'line' 'to' point=Point;
    Point: x=INT ',' y=INT;
    """

    # We will provide our class for Point.
    # Classes for other rules will be dynamically generated.
    class Point(object):
        def __init__(self, parent, x, y):
            self.parent = parent
            self.x = x
            self.y = y

        def __str__(self):
            return "{},{}".format(self.x, self.y)

        def __iadd__(self, other):
            self.x += other.x
            self.y += other.y
            return self

        def clone(self):
            return Point(self.parent, self.x, self.y)

    mm = metamodel_from_str(grammar, classes=[Point])

    model_str = """
        move to 5, 10
        line to 10, 10
        line to 20, 20
        move by 5, -7
        circle 10
        line to 10, 10
    """

    # Meta-model knows how to parse and instantiate models.
    model = mm.model_from_str(model_str)

    # At this point model is a plain Python object graph with instances of
    # dynamically created classes and attributes following the grammar.

    def cname(o):
        return o.__class__.__name__

    # Let's interpret the model
    position = Point(None, 0, 0)
    for command in model.commands:
        if cname(command) == 'MoveTo':
            print('Moving to position', command.position)
            position = command.position.clone()
        elif cname(command) == 'MoveBy':
            position += command.vector
            print('Moving by', command.vector, 'to a new position', position)
        elif cname(command) == 'Circle':
            print('Drawing circle at', position, 'with radius', command.radius)
        else:
            print('Drawing line from', position, 'to', command.point)
            position = command.point.clone()
    print('End position is', position)

    # Output:
    # Moving to position 5,10
    # Drawing line from 5,10 to 10,10
    # Drawing line from 10,10 to 20,20
    # Moving by 5,-7 to a new position 25,13
    # Drawing circle at 25,13 with radius 10
    # Drawing line from 25,13 to 10,10

    # Collect all points starting from the root of the model
    points = get_children_of_type("Point", model)
    for point in points:
        print('Point: {}'.format(point))

    # Output:
    # Point: 5,10
    # Point: 10,10
    # Point: 20,20
    # Point: 5,-7
    # Point: 10,10


if __name__ == '__main__':
    main()
